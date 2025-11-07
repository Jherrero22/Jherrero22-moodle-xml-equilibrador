#!/usr/bin/env python3
import argparse, random
from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import etree

def get_text_or_empty(soup_tag: Tag) -> str:
    if soup_tag is None:
        return ""
    t = soup_tag.find("text")
    return (t.get_text(" ", strip=True) if t else soup_tag.get_text(" ", strip=True))

def set_text_safely(soup, parent_tag: Tag, new_text: str):
    txt = parent_tag.find("text")
    if txt is None:
        txt = soup.new_tag("text")
        parent_tag.clear()
        parent_tag.append(txt)
    else:
        txt.clear()
    txt.append(new_text)

def wcount(s: str) -> int:
    return len([w for w in s.replace("\n"," ").split(" ") if w.strip()])

def equilibrar(infile, outxml, threshold, extension_txt, shuffle_answers, seed):
    if seed is not None:
        random.seed(seed)
    with open(infile, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "xml")

    questions = soup.find_all("question", {"type":"multichoice"})
    changed = 0

    for q in questions:
        answers = q.find_all("answer", recursive=False) or q.find_all("answer")
        if len(answers) != 3:
            continue

        # índice de la correcta
        correct_idx = next((i for i, a in enumerate(answers)
                            if a.get("fraction","0").strip() in ("100","100.0")), None)
        if correct_idx is None:
            continue

        # longitudes
        lens = [wcount(get_text_or_empty(a)) for a in answers]
        correct_len = lens[correct_idx]

        # ampliar incorrectas demasiado cortas
        extended_here = False
        for i, a in enumerate(answers):
            if i == correct_idx:
                continue
            if (correct_len - lens[i]) > threshold:
                base = get_text_or_empty(a)
                set_text_safely(soup, a, base + extension_txt)
                extended_here = True
        if extended_here:
            changed += 1

        # reordenar opciones reconstruyendo (más robusto)
        if shuffle_answers:
            payloads = [(get_text_or_empty(a), i==correct_idx) for i, a in enumerate(answers)]
            random.shuffle(payloads)
            for old in list(q.find_all("answer")):
                old.decompose()
            for a_txt, is_correct in payloads:
                new_ans = soup.new_tag("answer")
                new_ans.attrs["fraction"] = "100" if is_correct else "0"
                tnode = soup.new_tag("text"); tnode.string = a_txt
                new_ans.append(tnode)
                q.append(new_ans)

    # guardar XML con lxml (robusto)
    xml_str = str(soup)
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(xml_str.encode("utf-8"), parser=parser)
    xml_bytes = etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True)

    with open(outxml, "wb") as f:
        f.write(xml_bytes)

    print(f"✔ Guardado: {outxml} | Preguntas modificadas: {changed}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Equilibrar longitudes de opciones en Moodle XML.")
    p.add_argument("--infile", required=True, help="Ruta al XML de entrada")
    p.add_argument("--outxml", default="equilibrado.xml")
    p.add_argument("--threshold", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-shuffle", action="store_true", help="No barajar opciones")
    p.add_argument("--extension", default=(" Este matiz ha sido descrito en investigaciones sobre lectura, "
                                           "priming y competencia léxica en distintas poblaciones lectoras."))
    args = p.parse_args()

    equilibrar(
        infile=args.infile,
        outxml=args.outxml,
        threshold=args.threshold,
        extension_txt=args.extension,
        shuffle_answers=not args.no_shuffle,
        seed=args.seed
    )

