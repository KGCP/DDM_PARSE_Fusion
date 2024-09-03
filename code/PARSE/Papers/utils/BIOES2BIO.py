import csv

def bioes_to_bio(tag):
    if tag.startswith("B-") or tag.startswith("I-"):
        return tag
    elif tag.startswith("E-"):
        return "I-" + tag[2:]
    elif tag.startswith("S-"):
        return "B-" + tag[2:]
    else:
        return tag

def convert_bioes_to_bio(input_file, output_file):
    with open(input_file, "r", newline='', encoding='utf-8') as input_csv, open(output_file, "w", newline='', encoding='utf-8') as output_csv:
        reader = csv.reader(input_csv, delimiter='\t')
        writer = csv.writer(output_csv, delimiter='\t')

        for row in reader:
            if len(row) == 0:
                writer.writerow(row)
            elif len(row) == 2:
                token, tag = row
                new_tag = bioes_to_bio(tag)
                writer.writerow([token, new_tag])

if __name__ == "__main__":
    input_file = "../Models/models/dataset/test_title_v2.csv"
    output_file = "../Models/models/dataset/test_title_v3.csv"
    convert_bioes_to_bio(input_file, output_file)
