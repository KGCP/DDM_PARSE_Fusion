# -*- coding: utf-8 -*-
"""
md2ttl_v3_batch_hardpath.py

按你的要求：
- **不使用 argparse**，直接在文件顶部用常量显式写死/可手动改路径。
- 递归遍历 ROOT_MD_DIR 下所有 .md 文件，逐个生成 ttl 到 OUT_TTL_DIR。
- 其余逻辑与 md2ttl_v3_fullname_refnode_posint.py 一致（index 统一 positiveInteger，改进 title 提取）。
- 不做 owl:sameAs。

直接运行：
    python marker2ttl.py

如需改路径，直接改下面两个常量：
    ROOT_MD_DIR = "D:/Develop/DDM_PARSE_Fusion/data/markdown"
    OUT_TTL_DIR = "D:/Develop/DDM_PARSE_Fusion/output/ttl"
"""

import os
import re
import html
from hashlib import md5
from urllib.parse import quote
import xml.etree.ElementTree as ET
from typing import List, Dict, Set, Optional

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, DC, XSD

# -------------------- 路径常量（按需修改） --------------------
ROOT_MD_DIR = "D:/Develop/DDM_PARSE_Fusion/data/markdown"
OUT_TTL_DIR = "D:/Develop/DDM_PARSE_Fusion/output/ttl"

# -------------------- 命名空间 --------------------
ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
DOMO      = Namespace("http://data.anu.edu.au/def/ont/domo#")

NUMBER_OF_SENTENCES = "numberOfSentences"
HAS_CITATION        = "hasCitation"

# -------------------- 工具函数 --------------------
def clean_md_markup(text: str) -> str:
    return re.sub(r"[*_`]+", "", text)

def clean_text(t: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()

def clean_uri(t: str, limit: int = 80) -> str:
    base = re.sub(r"[^\w\s-]", "", t).lower().replace(" ", "_")
    return quote(base)[:limit] or md5(t.encode()).hexdigest()[:12]

def extract_paper_title(md: str) -> str:
    for ln in md.splitlines():
        if ln.startswith("# "):
            return clean_md_markup(ln[2:]).strip(' #:-')
    for ln in md.splitlines():
        if ln.strip():
            return clean_md_markup(ln).strip(' #:-')
    return "Untitled Paper"

# -------------------- 引用块解析 --------------------
_ref_heading_pat = re.compile(r"^(#{1,6})\s*(references?|bibliography|works\s+cited)\s*$", re.I | re.M)
_lead_num_pat    = re.compile(r"^\s*(\[(?P<n1>\d+)\]|(?P<n2>\d+)[.)])\s*")
_year_pat        = re.compile(r"(19|20)\d{2}")
_detail_pat      = re.compile(r"""
    ^\s*(?:\[(?P<i1>\d+)\]|(?P<i2>\d+)[.)])?\s*
    (?P<authors>.+?)\s*\(\s*(?P<year>(19|20)\d{2})\s*\)\.?\s*
    (?P<title>[^.]+?)\.\s*
""", re.X | re.S)

def extract_reference_block(md: str) -> str:
    for m in _ref_heading_pat.finditer(md):
        start = md.find("\n", m.start())
        rest  = md[start + 1:] if start != -1 else ""
        nxt   = re.search(r"^#{1,6}\s", rest, re.M)
        return rest[: (nxt.start() if nxt else len(rest))].strip()
    return ""

def split_ref_lines(block: str) -> List[str]:
    return [ln.strip() for ln in re.split(r'(?:\n|<br\s*/?>)+', block) if ln.strip()]

def group_references(lines: List[str]) -> List[str]:
    entries, buf = [], []
    for line in lines:
        if _lead_num_pat.match(line) and buf:
            entries.append(" ".join(buf).strip())
            buf = [line]
        else:
            buf.append(line)
    if buf:
        entries.append(" ".join(buf).strip())
    return entries

def guess_title_from_raw(raw_wo_lead: str, year_pos: int) -> str:
    after = raw_wo_lead[year_pos:] if year_pos >= 0 else raw_wo_lead
    after = after.lstrip(").,;: \t")
    dot = after.find('.')
    cand = after[:dot] if dot != -1 else after
    cand = clean_md_markup(cand).strip(' "')
    return cand[:200]

def refine_fields(raw: str) -> Dict:
    idx = None
    mlead = _lead_num_pat.match(raw)
    if mlead:
        idx = mlead.group('n1') or mlead.group('n2')
        content = raw[mlead.end():].strip()
    else:
        content = raw

    authors = title = ""
    year = ""

    m = _detail_pat.match(content)
    if m:
        d = m.groupdict()
        if not idx:
            idx = d.get('i1') or d.get('i2')
        authors = (d.get('authors') or '').strip(' .')
        year    = (d.get('year') or '').strip()
        title   = (d.get('title') or '').strip(' "')
    else:
        y = _year_pat.search(content)
        if y:
            year = y.group(0)
            title = guess_title_from_raw(content, y.end())
        if y:
            authors = content[:y.start()].strip(' .')

    return {
        'idx': idx,
        'year': year,
        'title': title,
        'authors': authors,
        'raw': clean_md_markup(raw)
    }

def parse_reference_block(block: str) -> List[Dict]:
    lines  = split_ref_lines(block)
    groups = group_references(lines)
    return [refine_fields(g) for g in groups]

# -------------------- 文内引用提取 --------------------
_num_pat  = re.compile(
    r"\[((?:\d+\s*(?:[\u2013\u2014\-]\s*\d+)?)"  # 13 or 13-15
    r"(?:\s*,\s*\d+\s*(?:[\u2013\u2014\-]\s*\d+)?)*)\]"
)
_range_pat = re.compile(r"(\d+)\s*[\u2013\u2014\-]\s*(\d+)")
_auth_pat  = re.compile(
    r"(?:^|\W)([A-Z][A-Za-z\-]+)(?:\s+et\s+al)?(?:\s+and\s+[A-Z][A-Za-z\-]+)?\s*(?:,|\(|\s)(\d{4})(?:\)|\b)"
)

def _expand_num(tok: str) -> List[str]:
    out = []
    for seg in tok.split(','):
        seg = seg.strip()
        m = _range_pat.fullmatch(seg)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.extend(map(str, range(a, b + 1)))
        elif seg:
            out.append(seg)
    return out

def extract_citations(txt: str) -> List[str]:
    cites, seen = [], set()
    for m in _num_pat.finditer(txt):
        for n in _expand_num(m.group(1)):
            if n not in seen:
                cites.append(n); seen.add(n)
    for m in _auth_pat.finditer(txt):
        key = f"{m.group(1).lower()}_{m.group(2)}"
        if key not in seen:
            cites.append(key); seen.add(key)
    return cites

# -------------------- Markdown → XML --------------------

def parse_markdown_structure(md: str):
    lines, secs, cur, buf = md.splitlines(), [], None, []
    for ln in lines:
        m = re.match(r"^(#{1,6})\s+(.+)$", ln)
        if m:
            if cur:
                cur['content'] = "\n".join(buf).strip(); secs.append(cur)
            cur = {'index': len(secs)+1, 'level': len(m.group(1)), 'title': m.group(2).strip()}
            buf = []
        elif cur is not None:
            buf.append(ln)
    if cur:
        cur['content'] = "\n".join(buf).strip(); secs.append(cur)
    return secs

split_paragraphs = lambda c: [p.strip() for p in re.split(r"\n\s*\n", c) if p.strip()]
split_sentences  = lambda p: [s for s in re.split(r"(?<=[.!?])\s+", clean_text(p)) if s]

def build_xml(md: str) -> ET.Element:
    root = ET.Element("root")
    for sec in parse_markdown_structure(md):
        sec_el = ET.SubElement(root, "section", ID=str(sec['index']),
                               index=str(sec['index']), level=str(sec['level']))
        ET.SubElement(sec_el, "heading").text = sec['title']
        sec_cnt = 0
        for pi, para in enumerate(split_paragraphs(sec['content']), 1):
            para_el = ET.SubElement(sec_el, "paragraph",
                                    ID=f"{sec['index']}.{pi}", index=str(pi))
            txt = clean_text(para)
            ET.SubElement(para_el, "text").text = txt
            for cit in extract_citations(txt):
                ET.SubElement(para_el, "citation").text = cit
            para_cnt = 0
            for si, s in enumerate(split_sentences(para), 1):
                sent_el = ET.SubElement(para_el, "sentence",
                                        ID=f"{sec['index']}.{pi}.{si}", index=str(si))
                ET.SubElement(sent_el, "text").text = s
                for cit in extract_citations(s):
                    ET.SubElement(sent_el, "citation").text = cit
                para_cnt += 1
            para_el.set("numberOfSentences", str(para_cnt)); sec_cnt += para_cnt
        sec_el.set("numberOfSentences", str(sec_cnt))
    return root

# -------------------- TTL 生成 --------------------

def generate_ttl(xml_root: ET.Element, md: str, out: str, paper_id: str):
    g = Graph()
    for p, ns in [("askg-data", ASKG_DATA), ("askg-onto", ASKG_ONTO), ("domo", DOMO)]:
        g.bind(p, ns)
    g.bind("rdfs", RDFS); g.bind("dc", DC); g.bind("xsd", XSD)

    idx_p    = URIRef(ASKG_ONTO + "index")
    lvl_p    = URIRef(ASKG_ONTO + "level")
    n_sent_p = URIRef(ASKG_ONTO + NUMBER_OF_SENTENCES)
    has_cit  = URIRef(ASKG_ONTO + HAS_CITATION)
    year_p   = URIRef(ASKG_ONTO + "year")

    # Paper
    paper_uri   = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}")
    paper_title = extract_paper_title(md)
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, DC.title,  Literal(paper_title, lang="en")))
    g.add((paper_uri, RDFS.label, Literal(paper_title, lang="en")))

    # References
    ref_block = extract_reference_block(md)
    refs      = parse_reference_block(ref_block)

    num_idx: Dict[str, URIRef] = {}
    ay_idx:  Dict[str, URIRef] = {}

    for ref in refs:
        real_idx = ref.get('idx')
        suffix   = real_idx if real_idx else md5(ref['raw'].encode()).hexdigest()[:8]
        ref_uri  = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Reference-{suffix}")

        g.add((ref_uri, RDF.type, ASKG_ONTO.Reference))
        g.add((ref_uri, RDFS.label, Literal(f"Reference {real_idx or suffix}", lang="en")))
        g.add((ref_uri, DOMO.Text, Literal(ref['raw'], lang="en")))

        if real_idx and real_idx.isdigit():
            g.add((ref_uri, idx_p, Literal(int(real_idx), datatype=XSD.positiveInteger)))
            num_idx[real_idx] = ref_uri

        if ref.get('year') and ref['year'].isdigit():
            g.add((ref_uri, year_p, Literal(int(ref['year']), datatype=XSD.positiveInteger)))

        if ref.get('title'):
            g.add((ref_uri, DC.title, Literal(ref['title'], lang="en")))
        else:
            raw = ref['raw']
            raw_wo_lead = _lead_num_pat.sub('', raw, count=1).strip()
            ymatch = _year_pat.search(raw_wo_lead)
            if ymatch:
                guess = guess_title_from_raw(raw_wo_lead, ymatch.end())
            else:
                dot = raw_wo_lead.find('.')
                guess = clean_md_markup(raw_wo_lead[:dot] if dot != -1 else raw_wo_lead).strip(' "')
            if guess:
                g.add((ref_uri, DC.title, Literal(guess, lang="en")))

        if ref.get('authors') and ref.get('year') and ref['year'].isdigit():
            surname = ref['authors'].split(',')[0].split()[-1].lower() if ',' in ref['authors'] else ref['authors'].split()[-1].lower()
            ay_idx[f"{surname}_{ref['year']}"] = ref_uri

    # Walk XML
    for sec in xml_root.findall("./section"):
        sid     = sec.get("ID")
        sec_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Section-{sid}")
        g.add((sec_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, sec_uri))
        g.add((sec_uri, RDFS.label, Literal(f"Section {sid}", lang="en")))
        g.add((sec_uri, idx_p,  Literal(int(sid), datatype=XSD.positiveInteger)))
        g.add((sec_uri, lvl_p,  Literal(int(sec.get("level")), datatype=XSD.int)))
        g.add((sec_uri, n_sent_p, Literal(int(sec.get(NUMBER_OF_SENTENCES)), datatype=XSD.positiveInteger)))
        g.add((sec_uri, DOMO.Text, Literal(sec.findtext("heading", ""), lang="en")))

        sec_seen: Set[URIRef] = set()

        for para in sec.findall("paragraph"):
            pid      = para.get("ID")
            para_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Section-{sid}-Paragraph-{clean_uri(pid)}")
            g.add((para_uri, RDF.type, ASKG_ONTO.Paragraph))
            g.add((sec_uri, ASKG_ONTO.hasParagraph, para_uri))
            g.add((para_uri, RDFS.label, Literal(f"Paragraph {para.get('index')}", lang="en")))
            g.add((para_uri, idx_p,  Literal(int(para.get("index")), datatype=XSD.positiveInteger)))
            g.add((para_uri, n_sent_p, Literal(int(para.get(NUMBER_OF_SENTENCES)), datatype=XSD.positiveInteger)))
            g.add((para_uri, DOMO.Text, Literal(para.findtext("text", ""), lang="en")))

            para_seen: Set[URIRef] = set()

            def _cite(tok: str) -> Optional[URIRef]:
                if tok.isdigit():
                    return num_idx.get(tok)
                return ay_idx.get(tok.lower())

            for tok in [c.text for c in para.findall("citation")]:
                obj = _cite(tok)
                if obj is None:
                    continue
                if obj not in para_seen:
                    g.add((para_uri, has_cit, obj)); para_seen.add(obj)
                if obj not in sec_seen:
                    g.add((sec_uri, has_cit, obj));  sec_seen.add(obj)

            for sent in para.findall("sentence"):
                s_id     = sent.get("ID")
                sent_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Section-{sid}-Paragraph-{clean_uri(pid)}-Sentence-{clean_uri(s_id)}")
                g.add((sent_uri, RDF.type, ASKG_ONTO.Sentence))
                g.add((para_uri, ASKG_ONTO.hasSentence, sent_uri))
                g.add((sent_uri, RDFS.label, Literal(f"Sentence {sent.get('index')}", lang="en")))
                g.add((sent_uri, idx_p, Literal(int(sent.get('index')), datatype=XSD.positiveInteger)))
                g.add((sent_uri, DOMO.Text, Literal(sent.findtext("text", ""), lang="en")))

                sent_seen: Set[URIRef] = set()
                for tok in [c.text for c in sent.findall("citation")]:
                    obj = _cite(tok)
                    if obj is None:
                        continue
                    if obj not in sent_seen:
                        g.add((sent_uri, has_cit, obj));   sent_seen.add(obj)
                    if obj not in para_seen:
                        g.add((para_uri, has_cit, obj));   para_seen.add(obj)
                    if obj not in sec_seen:
                        g.add((sec_uri, has_cit, obj));    sec_seen.add(obj)

    g.serialize(out, format="turtle")
    print("✓ TTL saved →", out)

# -------------------- 批量处理 --------------------

def find_md_files(indir: str) -> List[str]:
    md_files = []
    for root, _dirs, files in os.walk(indir):
        for f in files:
            if f.lower().endswith('.md'):
                md_files.append(os.path.join(root, f))
    return sorted(md_files)

def run_batch():
    os.makedirs(OUT_TTL_DIR, exist_ok=True)
    md_files = find_md_files(ROOT_MD_DIR)
    if not md_files:
        print("[INFO] No .md files found under", ROOT_MD_DIR)
        return
    for md_path in md_files:
        try:
            with open(md_path, encoding='utf-8') as f:
                md = f.read()
            xml_root = build_xml(md)
            pid = os.path.splitext(os.path.basename(md_path))[0]
            out_ttl = os.path.join(OUT_TTL_DIR, f"{pid}.ttl")
            generate_ttl(xml_root, md, out_ttl, pid)
        except Exception as e:
            print(f"[ERROR] {md_path}: {e}")

def main():
    run_batch()

if __name__ == '__main__':
    main()