import jsonlines

# read the file into memory
# path_remote = "/home/entitylinking/confluenceRWP/"
path_local = ""
file_name_raw = "reliefweb_corpus_raw_20160331.json"
path_ner_classifier = "stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz"
path_ner_jar = "stanford-ner-2017-06-09/stanford-ner.jar"
path = path_local + file_name_raw

# # write the file into jsonl format
# reliefweb_corpus_raw = json.loads(open(path).read()) # length: 504308
#
# with jsonlines.open("reliefweb_corpus_raw_20160331.jsonl", "w") as writer:
#     for i in reliefweb_corpus_raw:
#         writer.write(i)
#
# count_eng = 0 # 426016 english docs 84.48%
# with jsonlines.open("reliefweb_corpus_raw_20160331_eng.jsonl", "w") as writer:
#     for i in reliefweb_corpus_raw:
#         if "en" in i["lang"]:
#             writer.write(i)
#             count_eng += 1

# read in the jsonl file
st = StanfordNERTagger(path_local + path_ner_classifier, path_local + path_ner_jar)
# tagged_raw = {}
counter = 0
with jsonlines.open("reliefweb_corpus_raw_20160331_eng.jsonl") as reader:
    with jsonlines.open("eng_tagged_raw_reliefweb.jsonl", "w") as writer:
        for obj in reader:
            temp_obj = {}
            temp_obj[obj["id"]] = st.tag(obj["text"].split())
            # tagged_raw[obj["id"]] = st.tag(obj["text"].split())
            writer.write(temp_obj)
            counter += 1
            print "finished tagging " + str(counter) + " / 426016 docs"
            # logging.info("finished tagging " + str(counter) + " / 426016 docs")
            if counter % 5000 == 0:
                with open("back/" + str(counter), "w") as fi:
                    fi.write("ok")


# with open("tagged_raw.json", "w") as f:
#     json.dump(tagged_raw, f)

source = "eng_tagged_raw_reliefweb.jsonl"
destination = "eng_tagged_combined_reliefweb.jsonl"

with jsonlines.open("toy.jsonl") as reader:
    with jsonlines.open("toy_out.jsonl", "w") as writer:
        for obj in reader:
            key = obj.keys()[0]
            value = obj[key]

            temp_obj = {}
            length = len(obj[key])
            temp_obj[key] = []
            pointer = 0
            while pointer < length:
                if value[pointer][1] != "O":
                    temp_result = [value[pointer][0]]
                    ety_type = value[pointer][1]
                    pointer += 1
                    while value[pointer][1] == ety_type:
                        temp_result.append(value[pointer][0])
                        pointer += 1

                    temp_obj[key].append(' '.join(temp_result))
                else:
                    pointer += 1
            writer.write(temp_obj)
