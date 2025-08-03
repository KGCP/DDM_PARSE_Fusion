#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Clear DYLD_LIBRARY_PATH to avoid SSL library conflicts
if "DYLD_LIBRARY_PATH" in os.environ:
    del os.environ["DYLD_LIBRARY_PATH"]

import re, html, xml.etree.ElementTree as ET
from hashlib import md5
from urllib.parse import quote
from typing import Dict, List, Tuple, Set
import dotenv
import markdown
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, DC, XSD, OWL, SKOS
import utils

dotenv.load_dotenv()

# --------------------------------------------------------------------------- #
# Namespaces
ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
DOMO = Namespace("http://example.org/domo/")

NUMBER_OF_SENTENCES = "numberOfSentences"
HAS_CITATION = "hasCitation"

# --------------------------------------------------------------------------- #
# MEANINGFUL_TYPES - 专注于天文学和计算机科学领域
MEANINGFUL_TYPES = {
    "Person",
    "Researcher",
    "Scientist",
    "Author",
    "Organization",  
    # Academic Concepts
    "Algorithm",
    "Method",
    "Technique",
    "Framework",
    "Model",
    "Dataset",
    "Database",
    "Corpus",
    "Research Field",
    "Research Area",
    "Domain",
    "Theory",
    "Concept",
    "Paradigm",
    # Research Artifacts
    "Paper",
    "Publication",
    "Article",
    "Study",
    "Experiment",
    "Result",
    "Finding",
    "System",
    "Tool",
    "Software",
    "Platform",
    # Computer Science & Astronomy Terms (删除生物相关)
    "Technology",
    "Device",
    "Equipment",
    "Telescope",
    "Observatory",
    "Satellite",
    "Galaxy",
    "Star",
    "Planet",
    "Nebula",
    "Black Hole",
    "Neural Network",
    "Machine Learning",
    "Deep Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Programming Language",
    "Operating System",
    "Processor",
    "Memory",
    "Network",
    # Metrics and Measurements
    "Metric",
    "Measure",
    "Score",
    "Rate",
    "Index",
}

# --------------------------------------------------------------------------- #
# === 引用 / 参考文献辅助 ======================================================
# 使用第一段代码的正则表达式和逻辑
_ref_heading_pat = re.compile(
    r"^(#{1,6})\s*(references?|bibliography|works\s+cited)\s*$", re.I | re.M
)

_ref_pat = re.compile(r"""
    ^\s*
    (?P<lead>\[\d+\]|\d+[.)])?\s*      # [12]  或 12.
    (?P<authors>.+?)                   # 作者串（贪婪到年份前）
    \s*\(\s*(?P<year>\d{4})\s*\)\.     # (2023).
    \s*
    (?P<title>[^.]+?\.)                # 标题直到下一个句点
""", re.X)

_lead_num_pat = re.compile(r"\s*(?:\[(?P<num>\d+)\]|(?P<num2>\d+)[.)])")

_num_pat = re.compile(r"\[(\d+(?:[\u2013\u2014\-]\d+)?(?:,\s*\d+(?:[\u2013\u2014\-]\d+)?)*)\]")
_auth_pat = re.compile(
    r"(?:^|\W)([A-Z][A-Za-z\-]+)(?:\s+et\s+al)?(?:\s+and\s+[A-Z][A-Za-z\-]+)?\s*(?:,|\(|\s)(\d{4})(?:\)|\b)"
)

def _expand_num(tok: str) -> List[str]:
    out = []
    for seg in tok.split(','):
        seg = seg.strip()
        if re.search(r"[\u2013\u2014\-]", seg):
            a, b = re.split(r"[\u2013\u2014\-]", seg)
            out.extend(map(str, range(int(a), int(b) + 1)))
        else:
            out.append(seg)
    return out

def extract_citations(text: str) -> List[str]:
    cites, seen = [], set()
    for m in _num_pat.finditer(text):
        for n in _expand_num(m.group(1)):
            if n not in seen:
                cites.append(n); seen.add(n)
    for m in _auth_pat.finditer(text):
        key = f"{m.group(1).lower()}_{m.group(2)}"
        if key not in seen:
            cites.append(key); seen.add(key)
    return cites

def extract_reference_block(md: str) -> str:
    for m in _ref_heading_pat.finditer(md):
        start = md.find("\n", m.start())
        rest  = md[start + 1:] if start != -1 else ""
        nxt   = re.search(r"^#{1,6}\s", rest, re.M)
        end   = start + 1 + (nxt.start() if nxt else len(rest))
        return md[start + 1:end].strip()
    return ""

def _first_surname(authors: str) -> str:
    # 逗号优先
    if ',' in authors:
        return authors.split(',')[0].strip().split()[0]
    parts = authors.strip().split()
    return parts[0] if len(parts) == 1 else parts[-1]

def parse_reference_lines(block: str) -> List[Dict]:
    """
    将参考文献块拆分为行并解析。
    - 无论正则是否完全匹配，都尽量提取行首编号，填充到 idx 字段。
    - 其余字段缺失时留空，避免后续 KeyError。
    """
    refs: List[Dict] = []

    # 按换行或 <br/> 拆分
    for raw in re.split(r'(?:\n|<br\s*/?>)+', block):
        raw = raw.strip()
        if not raw:
            continue

        # 1) 先抓行首编号
        lead_m = _lead_num_pat.match(raw)
        idx_num = (lead_m.group("num") or lead_m.group("num2")) if lead_m else None

        # 2) 再用完整正则解析
        m = _ref_pat.match(raw)
        if m:                                   # 成功解析
            d = m.groupdict()
            refs.append({
                "idx":     idx_num or re.sub(r"[^\d]", "", d.get("lead") or "") or None,
                "authors": (d.get("authors") or "").strip(" ."),
                "year":    d.get("year") or "",
                "title":   (d.get("title") or "").strip(),
                "raw":     raw
            })
        else:                                  # 解析失败：至少保留 idx 与原始行
            refs.append({
                "idx":     idx_num,             # 可能是 None
                "authors": "",
                "year":    "",
                "title":   "",
                "raw":     raw
            })

    return refs

# --------------------------------------------------------------------------- #
# === 原清洗/分段/分句函数 =====================================================
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def split_into_paragraphs(content):
    return [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]


def split_into_sentences(text):
    return [
        s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text(text)) if s.strip()
    ]


def parse_markdown_structure(md_content):
    lines = md_content.split("\n")
    sections, cur, buf = [], None, []
    for ln in lines:
        m = re.match(r"^(#{1,6})\s+(.+)$", ln)
        if m:
            if cur:
                cur["content"] = "\n".join(buf).strip()
                sections.append(cur)
            cur = {
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
                "index": len(sections) + 1,
            }
            buf = []
        elif cur:
            buf.append(ln)
    if cur:
        cur["content"] = "\n".join(buf).strip()
        sections.append(cur)
    return sections


# --------------------------------------------------------------------------- #
# === build_document_structure（增 numberOfSentences & citation 标签）=========
def build_document_structure(md_content):
    doc = ET.Element("section")
    for sec in parse_markdown_structure(md_content):
        sec_el = ET.SubElement(
            doc,
            "section",
            ID=str(sec["index"]),
            index=str(sec["index"]),
            level=str(sec["level"]),
        )
        ET.SubElement(sec_el, "heading").text = sec["title"]

        sec_sent_cnt = 0
        for pi, para in enumerate(split_into_paragraphs(sec["content"]), 1):
            para_el = ET.SubElement(
                sec_el, "paragraph", ID=f"{sec['index']}.{pi}", index=str(pi)
            )
            ET.SubElement(para_el, "text").text = clean_text(para)

            # 标注段落级引用
            for cit in extract_citations(para):
                ET.SubElement(para_el, "citation").text = cit

            para_sent_cnt = 0
            for si, sent in enumerate(split_into_sentences(para), 1):
                sent_el = ET.SubElement(
                    para_el, "sentence", ID=f"{sec['index']}.{pi}.{si}", index=str(si)
                )
                ET.SubElement(sent_el, "text").text = sent
                for cit in extract_citations(sent):
                    ET.SubElement(sent_el, "citation").text = cit
                para_sent_cnt += 1

            para_el.set(NUMBER_OF_SENTENCES, str(para_sent_cnt))
            sec_sent_cnt += para_sent_cnt
        sec_el.set(NUMBER_OF_SENTENCES, str(sec_sent_cnt))
    return doc


# --------------------------------------------------------------------------- #
# === Helper =================================================================
def _clean_uri(text: str, max_len: int = 80) -> str:
    base = re.sub(r"[^\w\s-]", "", text).lower().replace(" ", "_")
    base = quote(base)[:max_len]
    return base or md5(text.encode()).hexdigest()[:12]

# 使用第一段代码的简化逻辑
def clean_uri(t: str, limit=80) -> str:
    base = re.sub(r"[^\w\s-]", "", t).lower().replace(" ", "_")
    return quote(base)[:limit] or md5(t.encode()).hexdigest()[:12]

# --------------------------------------------------------------------------- #
# === generate_ttl（使用第一段代码的引用处理逻辑）===============================
def generate_ttl(doc, output_file, paper_id, md_content, existing_papers=None):
    print(f"  - Generating TTL for paper: {paper_id}")
    g = Graph()
    for p, ns in [("askg-data", ASKG_DATA), ("askg-onto", ASKG_ONTO), ("domo", DOMO)]:
        g.bind(p, ns)
    g.bind("rdfs", RDFS)
    g.bind("dc", DC)
    g.bind("xsd", XSD)

    # Predicates
    idx_p = URIRef(ASKG_ONTO + "index")
    lvl_p = URIRef(ASKG_ONTO + "level")
    n_sent_p = URIRef(ASKG_ONTO + NUMBER_OF_SENTENCES)
    has_cit_p = URIRef(ASKG_ONTO + HAS_CITATION)
    mentions_p = URIRef(ASKG_ONTO + "mentions")
    in_sent_p = URIRef(ASKG_ONTO + "inSentence")
    ent_type_p = URIRef(ASKG_ONTO + "entityType")
    author_p = URIRef(ASKG_ONTO + "author")

    # ---- Paper ----
    paper_uri   = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}")
    paper_title = next((l[2:].strip() for l in md_content.splitlines() if l.startswith("# ")), paper_id)
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, DC.title,  Literal(paper_title, lang="en")))
    g.add((paper_uri, RDFS.label, Literal(paper_title, lang="en")))

    # ---- References ----
    ref_block = extract_reference_block(md_content)
    refs      = parse_reference_lines(ref_block)
    num_idx: Dict[str, URIRef] = {}
    ay_idx:  Dict[str, URIRef] = {}

    for i, ref in enumerate(refs, 1):
        ref_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Reference-{i}")
        g.add((ref_uri, RDF.type, ASKG_ONTO.Reference))
        g.add((ref_uri, RDFS.label, Literal(f"Reference {i}", lang="en")))
        g.add((ref_uri, DOMO.Text, Literal(ref["raw"], lang="en")))

        # ★ 使用 .get() 并确保字段存在
        authors = ref.get("authors", "")
        year    = ref.get("year", "")

        if re.search(r"[A-Za-z]", authors):
            g.add((ref_uri, author_p, Literal(authors, lang="en")))
            if year:
                g.add((ref_uri, DC.date, Literal(year, datatype=XSD.gYear)))
                surname = _first_surname(authors).lower()
                ay_idx[f"{surname}_{year}"] = ref_uri

        idx_num = ref.get("idx")
        if idx_num:
            num_idx[idx_num] = ref_uri

    # ---- Walk XML ----
    for sec in doc.findall("./section"):
        sid     = sec.get("ID")
        sec_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Section-{sid}")
        g.add((sec_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, sec_uri))
        g.add((sec_uri, RDFS.label, Literal(f"Section {sid}", lang="en")))
        g.add((sec_uri, idx_p,  Literal(sid, datatype=XSD.int)))
        g.add((sec_uri, lvl_p,  Literal(sec.get("level"), datatype=XSD.int)))
        g.add((sec_uri, n_sent_p, Literal(sec.get(NUMBER_OF_SENTENCES), datatype=XSD.positiveInteger)))
        hd = sec.find("heading");  hd_text = hd.text if hd is not None else ""
        g.add((sec_uri, DOMO.Text, Literal(hd_text, lang="en")))

        sec_seen: Set[URIRef] = set()

        for para in sec.findall("paragraph"):
            pid      = para.get("ID")
            para_uri = URIRef(ASKG_DATA + f"Paper-{clean_uri(paper_id)}-Section-{sid}-Paragraph-{clean_uri(pid)}")
            g.add((para_uri, RDF.type, ASKG_ONTO.Paragraph))
            g.add((sec_uri, ASKG_ONTO.hasParagraph, para_uri))
            g.add((para_uri, RDFS.label, Literal(f"Paragraph {para.get('index')}", lang="en")))
            g.add((para_uri, idx_p,  Literal(para.get("index"), datatype=XSD.int)))
            g.add((para_uri, n_sent_p, Literal(para.get(NUMBER_OF_SENTENCES), datatype=XSD.positiveInteger)))
            p_txt = para.findtext("text", "")
            g.add((para_uri, DOMO.Text, Literal(p_txt, lang="en")))

            para_seen: Set[URIRef] = set()

            def _cite(token: str):
                if token.isdigit():
                    return num_idx.get(token)
                return ay_idx.get(token.lower())

            for tok in [c.text for c in para.findall("citation")]:
                obj = _cite(tok) or Literal(tok.replace("_", " "))
                if obj not in para_seen:
                    g.add((para_uri, has_cit_p, obj)); para_seen.add(obj)
                if obj not in sec_seen:
                    g.add((sec_uri, has_cit_p, obj));  sec_seen.add(obj)

            for sent in para.findall("sentence"):
                s_id     = sent.get("ID")
                sent_uri = URIRef(
                    ASKG_DATA +
                    f"Paper-{clean_uri(paper_id)}-Section-{sid}-Paragraph-{clean_uri(pid)}-Sentence-{clean_uri(s_id)}")
                g.add((sent_uri, RDF.type, ASKG_ONTO.Sentence))
                g.add((para_uri, ASKG_ONTO.hasSentence, sent_uri))
                g.add((sent_uri, RDFS.label, Literal(f"Sentence {sent.get('index')}", lang="en")))
                g.add((sent_uri, idx_p, Literal(sent.get('index'), datatype=XSD.int)))
                s_txt = sent.findtext("text")
                g.add((sent_uri, DOMO.Text, Literal(s_txt, lang="en")))

                sent_seen: Set[URIRef] = set()
                for tok in [c.text for c in sent.findall("citation")]:
                    obj = _cite(tok) or Literal(tok.replace("_", " "))
                    if obj not in sent_seen:
                        g.add((sent_uri, has_cit_p, obj));   sent_seen.add(obj)
                    if obj not in para_seen:
                        g.add((para_uri, has_cit_p, obj));   para_seen.add(obj)
                    if obj not in sec_seen:
                        g.add((sec_uri, has_cit_p, obj));    sec_seen.add(obj)

                # 添加句子文本
                g.add((sent_uri, in_sent_p, Literal(s_txt, datatype=XSD.string)))

                # 实体抽取（可选，如果失败则跳过）
                try:
                    if ENABLE_ENTITY_EXTRACTION:
                        print(f"    🔍 Extracting entities from sentence: {s_id}")
                        print(
                            f"       Text: {s_txt[:100]}{'...' if len(s_txt) > 100 else ''}"
                        )
                        ents, has_ents = utils.get_entities(s_txt)
                        if has_ents:
                            print(f"    ✓ Found {len(ents)} entities:")
                            for i, e in enumerate(ents, 1):
                                print(
                                    f"      {i}. {e.head} ({e.head_type}) --{e.relation}--> {e.tail} ({e.tail_type})"
                                )
                                if e.head_type in MEANINGFUL_TYPES:
                                    h_uri = URIRef(
                                        ASKG_DATA + f"Entity-{clean_uri(e.head)}"
                                    )
                                    g.add((sent_uri, mentions_p, h_uri))
                                    g.add(
                                        (h_uri, RDFS.label, Literal(e.head, lang="en"))
                                    )
                                    g.add(
                                        (
                                            h_uri,
                                            ent_type_p,
                                            Literal(e.head_type, lang="en"),
                                        )
                                    )
                                if e.tail_type in MEANINGFUL_TYPES:
                                    t_uri = URIRef(
                                        ASKG_DATA + f"Entity-{clean_uri(e.tail)}"
                                    )
                                    g.add((sent_uri, mentions_p, t_uri))
                                    g.add(
                                        (t_uri, RDFS.label, Literal(e.tail, lang="en"))
                                    )
                                    g.add(
                                        (
                                            t_uri,
                                            ent_type_p,
                                            Literal(e.tail_type, lang="en"),
                                        )
                                    )
                        else:
                            print(f"    - No entities found in this sentence")
                except Exception as e:
                    print(
                        f"    Warning: Entity extraction failed for sentence (continuing without entities): {str(e)[:100]}"
                    )

    g.serialize(destination=output_file, format="turtle")
    print("✓ TTL saved:", output_file)


# --------------------------------------------------------------------------- #
# 其余流程保持不变 -------------------------------------------------------------
def process_markdown_file(input_file, output_ttl, paper_id=None, existing_papers=None):
    print(f"  - Reading file: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    print(f"  - File size: {len(md_content)} characters")

    if paper_id is None:
        paper_id = os.path.splitext(os.path.basename(input_file))[0]

    print(f"  - Building document structure...")
    doc = build_document_structure(md_content)

    print(f"  - Generating TTL file: {output_ttl}")
    generate_ttl(doc, output_ttl, paper_id, md_content, existing_papers)


def process_all_markdown_files(input_dir="./markdown", output_dir="./output"):
    print(f"Creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Checking for markdown files in: {input_dir}")
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist!")
        return

    md_files = [f for f in os.listdir(input_dir) if f.endswith(".md")]
    print(f"Found {len(md_files)} markdown files")

    if not md_files:
        print(f"No markdown files found in {input_dir}")
        return

    for i, md_file in enumerate(md_files, 1):
        print(f"Processing file {i}/{len(md_files)}: {md_file}")
        in_path = os.path.join(input_dir, md_file)
        out_path = os.path.join(output_dir, f"{os.path.splitext(md_file)[0]}.ttl")
        try:
            process_markdown_file(in_path, out_path)
            print(f"✓ Successfully processed: {md_file}")
        except Exception as e:
            print(f"✗ Error processing {md_file}: {str(e)}")
            import traceback

            traceback.print_exc()


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # 检查OpenAI API配置
    print("Checking OpenAI API configuration...")
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Entity extraction will be skipped if it fails.")
        print("To enable entity extraction, set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print()
    else:
        print("✓ OpenAI API key found")
        print()

    # 设置默认的输入和输出目录 - 使用相对于脚本文件的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "markdown", "test")
    output_dir = os.path.join(script_dir, "output", "test")

    print(f"Processing markdown files from: {input_dir}")
    print(f"Output TTL files to: {output_dir}")

    # Entity extraction toggle (set environment variable ENABLE_ENTITY_EXTRACTION=1 to enable)
    ENABLE_ENTITY_EXTRACTION = os.environ.get("ENABLE_ENTITY_EXTRACTION", "1") == "1"

    process_all_markdown_files(input_dir, output_dir)