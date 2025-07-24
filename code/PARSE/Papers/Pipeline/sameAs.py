# -*- coding: utf-8 -*-
"""

Post-processing script to add `owl:sameAs` triples from Reference nodes
in TTL files to existing Paper nodes, using hard-coded paths.

Workflow:
1. Build an index of all Paper titles (normalized) from every TTL in INPUT_DIR.
2. For each TTL file, for each Reference (ASKG_ONTO.Reference), take its domo:Text,
   normalize, and fuzzy-match it against the Paper-title index.
3. If the best match is confident (score ≥ THRESHOLD and margin gap ≥ MARGIN),
   optionally re-check year, then add:
       <ref_uri> owl:sameAs <paper_uri>
4. Serialize the updated TTL to OUTPUT_DIR.
5. Print total matches and record detailed entries to RECORD_FILE.

"""

import os
import re
from typing import Dict, List, Tuple, Optional

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, DC, OWL, XSD
from tqdm import tqdm

# -------------------- Hard-coded paths & parameters --------------------
INPUT_DIR   = "/home/rujia/Data/marker/CS_ttl"
OUTPUT_DIR  = "/home/rujia/Data/marker/CS_matchedFiles"
RECORD_FILE = "/home/rujia/Data/marker/CS_ttl_matchedFiles"
THRESHOLD   = 90  # fuzzy-match score threshold (0–100)
MARGIN      = 5   # min diff between best and second-best scores

# -------------------- Namespaces --------------------
ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
DOMO      = Namespace("http://data.anu.edu.au/def/ont/domo#")

# -------------------- Utilities --------------------

def clean_md_markup(text: str) -> str:
    return re.sub(r"[*_`]+", "", text)

def normalize_title(t: str) -> str:
    t = clean_md_markup(str(t)).lower()
    t = re.sub(r"[^a-z0-9\s]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()

year_pat = re.compile(r"(19|20)\d{2}")

try:
    from rapidfuzz import process, fuzz
    _HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    _HAS_RAPIDFUZZ = False

# -------------------- Build Paper index --------------------
def build_paper_index(indir: str) -> Tuple[Dict[str, List[Tuple[URIRef, Optional[int]]]], List[str]]:
    """
    Load all TTLs in indir; index norm_title -> list of (paper_uri, year)
    Returns index and list of file paths.
    """
    idx: Dict[str, List[Tuple[URIRef, Optional[int]]]] = {}
    files = [os.path.join(indir, f) for f in os.listdir(indir) if f.endswith('.ttl')]
    for fn in files:
        g = Graph()
        try:
            g.parse(fn, format='turtle')
        except Exception as e:
            print(f"[WARN] cannot parse {fn}: {e}")
            continue
        for s in g.subjects(RDF.type, ASKG_ONTO.Paper):
            title = g.value(s, DC.title)
            if not title: continue
            norm = normalize_title(str(title))
            y = g.value(s, ASKG_ONTO.year)
            year = int(y) if isinstance(y, Literal) and y.datatype in (XSD.int, XSD.positiveInteger) else None
            idx.setdefault(norm, []).append((s, year))
    return idx, files

# -------------------- Matching helper --------------------
def best_match(query: str, candidates: List[str], threshold: int, margin: int) -> Optional[str]:
    """Return best_key if match is confident."""
    if not candidates:
        return None
    if _HAS_RAPIDFUZZ:
        res = process.extract(query, candidates, scorer=fuzz.token_set_ratio, limit=2)
        if not res: return None
        best_key, best_score = res[0][0], int(res[0][1])
        second = int(res[1][1]) if len(res)>1 else -1
        if best_score>=threshold and (best_score-second)>=margin:
            return best_key
    else:
        close = difflib.get_close_matches(query, candidates, n=2, cutoff=threshold/100.0)
        if not close: return None
        best_key = close[0]
        return best_key
    return None

# -------------------- Process one file --------------------
def process_file(fn: str, index: Dict[str, List[Tuple[URIRef, Optional[int]]]]) -> Tuple[int, List[str]]:
    """Add sameAs triples in graph; return number added and detail lines."""
    g = Graph(); g.parse(fn, format='turtle')
    count = 0; details: List[str] = []
    keys = list(index.keys())
    for ref in g.subjects(RDF.type, ASKG_ONTO.Reference):
        if list(g.objects(ref, OWL.sameAs)): continue
        raw = g.value(ref, DOMO.Text); txt = str(raw) if raw else ''
        norm = normalize_title(txt)
        year_m = year_pat.search(txt); ryear = int(year_m.group(0)) if year_m else None
        best = best_match(norm, keys, THRESHOLD, MARGIN)
        if not best: continue
        # choose candidate
        cand = index[best]
        uri = None
        if ryear is not None:
            for u, y in cand:
                if y is None or y==ryear:
                    uri = u; break
        if uri is None and cand:
            uri = cand[0][0]
        if uri:
            g.add((ref, OWL.sameAs, uri)); count+=1
            details.append(f"{os.path.basename(fn)}\t{ref}\t{uri}")
    if count>0:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        g.serialize(os.path.join(OUTPUT_DIR, os.path.basename(fn)), format='turtle')
    return count, details

# -------------------- Main --------------------
if __name__ == '__main__':
    index, files = build_paper_index(INPUT_DIR)
    total = 0; all_details: List[str] = []
    for fn in tqdm(files, desc="Processing TTL files", unit="file"):
        c, d = process_file(fn, index)
        total += c; all_details.extend(d)
        print(f"{os.path.basename(fn)}: +{c} sameAs")
    print(f"Total sameAs added: {total}")
    # write record
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        for line in all_details:
            f.write(line + '\n')
    print(f"Recorded matches at: {RECORD_FILE}")
