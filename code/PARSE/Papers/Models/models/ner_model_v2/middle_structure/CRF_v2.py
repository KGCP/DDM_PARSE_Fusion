"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 19/10/2022 9:33 pm
"""
from __future__ import print_function

import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F


class CRF(nn.Module):

    def __init__(self, tagset_size, gpu):
        super(CRF, self).__init__()

        # for torch scripting
        self.start_tag = -2
        self.stop_tag = -1

        self.gpu = gpu
        # Matrix of transition parameters.  Entry i,j is the score of transitioning from i to j.
        self.tagset_size = tagset_size
        # # We add 2 here, because of START_TAG and STOP_TAG
        # # transitions (f_tag_size, t_tag_size), transition value from f_tag to t_tag
        init_transitions = torch.zeros(self.tagset_size + 2, self.tagset_size + 2)
        init_transitions[:, self.start_tag] = -10000.0
        init_transitions[self.stop_tag, :] = -10000.0
        init_transitions[:, 0] = -10000.0
        init_transitions[0, :] = -10000.0

        if self.gpu:
            init_transitions = init_transitions.cuda()

        self.transitions = nn.Parameter(init_transitions)

    def forward(self, feats, mask, nbest):
        """
            input:
                feats: (batch, seq_len, self.tag_size+2)
                mask: (batch, seq_len)
            output:
                decode_idx: (batch, nbest, seq_len) decoded sequence
                path_score: (batch, nbest) corresponding score for each sequence (to be implementated)
                nbest decode for sentence with one token is not well supported, to be optimized
        """
        batch_size = feats.size(0)
        seq_len = feats.size(1)
        tag_size = feats.size(2)
        assert(tag_size == self.tagset_size+2)

        # calculate sentence length for each sentence
        length_mask = torch.sum(mask.long(), dim=1).view(batch_size, 1).long()

        # mask to (seq_len, batch_size)
        mask = mask.transpose(1, 0).contiguous()
        ins_num = seq_len * batch_size

        # be careful the view shape, it is .view(ins_num, 1, tag_size) but not .view(ins_num, tag_size, 1)
        feats = feats.transpose(1, 0).contiguous().view(ins_num, 1, tag_size).expand(ins_num, tag_size, tag_size)

        # need to consider start
        scores = feats + self.transitions.view(1,tag_size,tag_size).expand(ins_num, tag_size, tag_size)
        scores = scores.view(seq_len, batch_size, tag_size, tag_size)

        # build iter
        seq_iter = enumerate(scores)

        # record the position of best score
        back_points = list()
        partition_history = list()

        #  reverse mask (bug for mask = 1- mask, use this as alternative choice)
        # mask = 1 + (-1) * mask
        mask = (1 - mask.long()).to(torch.bool)
        if torch.jit.is_scripting():
            _, inivalues = 0, scores[0]  # bat_size * from_target_size * to_target_size:
        else:
            _, inivalues = next(seq_iter)

        # only need start from start_tag
        partition = inivalues[:, self.start_tag, :].clone()  # bat_size * to_target_size

        # initial partition [batch_size, tag_size]
        partition_history.append(partition.view(batch_size, tag_size, 1).expand(batch_size, tag_size, nbest))

        # iter over last scores
        for idx, cur_values in seq_iter:

            if torch.jit.is_scripting():
                if idx == 0:
                    continue

            if idx == 1:
                cur_values = cur_values.view(batch_size, tag_size, tag_size) + partition.contiguous().view(batch_size, tag_size, 1).expand(batch_size, tag_size, tag_size)
            else:
                # previous to_target is current from_target
                # partition: previous results log(exp(from_target)), #(batch_size * nbest * from_target)
                # cur_values: batch_size * from_target * to_target
                cur_values = cur_values.view(batch_size, tag_size, 1, tag_size).expand(batch_size, tag_size, nbest, tag_size) + partition.contiguous().view(batch_size, tag_size, nbest, 1).expand(batch_size, tag_size, nbest, tag_size)

                # compare all nbest and all from target
                cur_values = cur_values.view(batch_size, tag_size*nbest, tag_size)

            partition, cur_bp = torch.topk(cur_values, nbest, 1)

            # cur_bp/partition: [batch_size, nbest, tag_size], id should be normize through nbest in following backtrace step
            # print partition[:,0,:]
            # print cur_bp[:,0,:]
            # print "nbest, ",idx
            if idx == 1:
                cur_bp = cur_bp*nbest

            partition = partition.transpose(2, 1)
            cur_bp = cur_bp.transpose(2, 1)

            # partition: (batch_size * to_target * nbest)
            # cur_bp: (batch_size * to_target * nbest) Notice the cur_bp number is the whole position of tag_size*nbest, need to convert when decode
            partition_history.append(partition)

            # cur_bp: (batch_size,nbest, tag_size) topn source score position in current tag
            # set padded label as 0, which will be filtered in post processing
            # mask[idx] ? mask[idx-1]
            cur_bp.masked_fill_(mask[idx].view(batch_size, 1, 1).expand(batch_size, tag_size, nbest), 0)

            # print cur_bp[0]
            back_points.append(cur_bp)

        # add score to final STOP_TAG
        partition_history = torch.cat(partition_history, 0).view(seq_len, batch_size, tag_size, nbest).transpose(1,0).contiguous() ## (batch_size, seq_len, nbest, tag_size)

        # get the last position for each setences, and select the last partitions using gather()
        last_position = length_mask.view(batch_size, 1, 1, 1).expand(batch_size, 1, tag_size, nbest) - 1
        last_partition = torch.gather(partition_history, 1, last_position).view(batch_size, tag_size, nbest, 1)

        # calculate the score from last partition to end state (and then select the STOP_TAG from it)
        last_values = last_partition.expand(batch_size, tag_size, nbest, tag_size) + self.transitions.view(1, tag_size, 1, tag_size).expand(batch_size, tag_size, nbest, tag_size)
        last_values = last_values.view(batch_size, tag_size*nbest, tag_size)
        end_partition, end_bp = torch.topk(last_values, nbest, 1)

        # end_partition: (batch, nbest, tag_size)
        end_bp = end_bp.transpose(2, 1)

        # end_bp: (batch, tag_size, nbest)
        if torch.jit.is_scripting():
            pad_zero = torch.zeros(batch_size, tag_size, nbest).long()
        else:
            pad_zero = autograd.Variable(torch.zeros(batch_size, tag_size, nbest)).long()

        if self.gpu:
            pad_zero = pad_zero.cuda()

        back_points.append(pad_zero)
        back_points = torch.cat(back_points).view(seq_len, batch_size, tag_size, nbest)

        # select end ids in STOP_TAG
        pointer = end_bp[:, self.stop_tag, :] ##(batch_size, nbest)
        insert_last = pointer.contiguous().view(batch_size, 1, 1, nbest).expand(batch_size, 1, tag_size, nbest)
        back_points = back_points.transpose(1,0).contiguous()

        # move the end ids(expand to tag_size) to the corresponding position of back_points to replace the 0 values
        # print "lp:",last_position
        # print "il:",insert_last[0]
        # exit(0)
        # copy the ids of last position:insert_last to back_points, though the last_position index
        # last_position includes the length of batch sentences
        # print "old:", back_points[9,0,:,:]
        back_points.scatter_(1, last_position, insert_last)

        # back_points: [batch_size, seq_length, tag_size, nbest]
        # print "new:", back_points[9,0,:,:]
        # exit(0)
        # print pointer[2]
        '''
        back_points: in simple demonstratration
        x,x,x,x,x,x,x,x,x,7
        x,x,x,x,x,4,0,0,0,0
        x,x,6,0,0,0,0,0,0,0
        '''

        back_points = back_points.transpose(1, 0).contiguous()

        # print back_points[0]
        # back_points: (seq_len, batch, tag_size, nbest)
        # decode from the end, padded position ids are 0, which will be filtered in following evaluation
        if torch.jit.is_scripting():
            decode_idx = torch.empty(seq_len, batch_size, nbest, dtype=torch.int64)
        else:
            decode_idx = autograd.Variable(torch.LongTensor(seq_len, batch_size, nbest))

        if self.gpu:
            decode_idx = decode_idx.cuda()

        decode_idx[-1] = pointer.data/nbest
        # print "pointer-1:",pointer[2]
        # exit(0)
        # use old mask, let 0 means has token

        for idx in range(len(back_points) - 2, -1, -1):
            # print "pointer: ",idx,  pointer[3]
            # print "back:",back_points[idx][3]
            # print "mask:",mask[idx+1,3]
            new_pointer = torch.gather(back_points[idx].view(batch_size, tag_size*nbest), 1, pointer.contiguous().view(batch_size,nbest))
            decode_idx[idx] = new_pointer.data/nbest
            # # use new pointer to remember the last end nbest ids for non longest
            pointer = new_pointer + pointer.contiguous().view(batch_size, nbest)*mask[idx].view(batch_size, 1).expand(batch_size, nbest).long()

        # exit(0)
        path_score = None
        decode_idx = decode_idx.transpose(1, 0)
        # decode_idx: [batch, seq_len, nbest]
        # print decode_idx[:,:,0]
        # print "nbest:",nbest
        # print "diff:", decode_idx[:,:,0]- decode_idx[:,:,4]
        # print decode_idx[:,0,:]
        # exit(0)

        # calculate probability for each sequence
        scores = end_partition[:, :, self.stop_tag]
        ## scores: [batch_size, nbest]
        max_scores, _ = torch.max(scores, 1)
        minus_scores = scores - max_scores.view(batch_size, 1).expand(batch_size, nbest)
        path_score = F.softmax(minus_scores, 1)
        # path_score: [batch_size, nbest]
        # exit(0)

        return path_score, decode_idx