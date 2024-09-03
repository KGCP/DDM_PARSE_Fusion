import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from bert_score import score


def calculate_bleu(reference, candidate):
    reference = [reference.split()]
    candidate = candidate.split()
    return sentence_bleu(reference, candidate)


def calculate_rouge(reference, candidate):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    return scorer.score(reference, candidate)


def calculate_meteor(reference, candidate):
    return meteor_score([reference], candidate)


def calculate_bertscore(refs, cands):
    P, R, F1 = score(cands, refs, lang="en", verbose=True)
    return P.mean().item(), R.mean().item(), F1.mean().item()


def main():
    # 标准答案
    reference_text = "Along with each mapping, one can specify the target endpoint and graph.Target endpoint is a label that identifies a SPARQL endpoint access13 where the triples will be created.Examples: test, prod.Target graph is the named graph where the triples will be created.It is defined as a namespace prefix in the ontology file.Examples: g0-testing, g0-prod.The namespace prefix IRI will be used as the named graph for the triple creation for that specific mapping."
    # LLM生成的答案
    candidate_text = "The choice of target endpoint and named graph significantly impacts the efficiency and accuracy of data integration in distributed SPARQL endpoints. The target endpoint is a label that identifies a SPARQL endpoint where triples will be created, while the named graph is the namespace prefix in the ontology file that defines the graph where triples will be created. The correct selection of these parameters ensures that data is correctly integrated and processed, whereas incorrect choices can lead to errors or inconsistencies. For instance, if the target endpoint is set to test instead of prod, it may result in incorrect data being written to the production environment. Similarly, if the named graph is not correctly defined, it may lead to issues with data retrieval or processing. Therefore, careful consideration of these parameters is crucial for ensuring the accuracy and efficiency of data integration in distributed SPARQL endpoints."

    # 计算BLEU分数
    bleu_score = calculate_bleu(reference_text, candidate_text)
    print("BLEU Score:", bleu_score)

    # 计算ROUGE分数
    rouge_scores = calculate_rouge(reference_text, candidate_text)
    print("ROUGE Scores:", rouge_scores)

    # 计算METEOR分数
    meteor_score = calculate_meteor(reference_text, candidate_text)
    print("METEOR Score:", meteor_score)

    # 计算BERTScore
    P, R, F1 = calculate_bertscore([reference_text], [candidate_text])
    print("BERTScore Precision:", P)
    print("BERTScore Recall:", R)
    print("BERTScore F1:", F1)


if __name__ == "__main__":
    main()
