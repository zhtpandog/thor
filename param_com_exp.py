import json
import os
import codecs
import operator
from sklearn.model_selection import KFold
import numpy as np

config = json.loads(open("config.json").read())

X_data_labeled = config["X_data_labeled"]
X_data_unlabeled = config["X_data_unlabeled"]
y_data = config["y_data"]
id_data = config["id_data"]
param_dict = config["param_dict"]
num_labels = config["num_labels"]
fasttext_dir = config["fasttext_dir"]

X_labeled = json.loads(open(X_data_labeled).read()) # with \n in the end of each line
X_unlabeled = json.loads(open(X_data_unlabeled).read()) # no \n in the end of each line
y = json.loads(open(y_data).read())
id = json.loads(open(id_data).read())

def ndcg_score(pred_labels, corr_labels):
    scores = [0 for i in pred_labels]
    for i in corr_labels:
        scores[pred_labels.index(i)] = 1
    dcg = 0
    for idx, score in enumerate(scores):
        dcg += score / np.log2(idx + 1 + 1)
    scores.sort(reverse=True)
    idcg = 0
    for idx, score in enumerate(scores):
        if score == 0:
            break
        idcg += score / np.log2(idx + 1 + 1)
    ndcg = dcg / idcg
    return ndcg

def get_param_comb_list(param):
    # see if there is any proprocess commands
    prepro = []
    if "preprocess" in param:
        prepro = param["preprocess"]
        del param["preprocess"]

    # get param combinations
    num_param = len(param)

    if prepro:
        param_tokens = ["a"] + [chr(ord("b") + i) for i in range(num_param)]
    else:
        param_tokens = [chr(ord("a") + i) for i in range(num_param)]

    comb_cmd = ["[", "(" + ",".join(param_tokens) + ")"]
    param_items = param.items()
    param_cates = []
    if prepro:
        param_cates.append("preprocess")
        comb_cmd.append(" for ")
        comb_cmd.append(param_tokens[0])
        comb_cmd.append(" in ")
        comb_cmd.append(str(prepro))

        for idx, content in enumerate(param_items):
            param_cates.append(content[0])
            comb_cmd.append(" for ")
            comb_cmd.append(param_tokens[idx + 1])
            comb_cmd.append(" in ")
            comb_cmd.append(str(content[1]))
    else:
        for idx, content in enumerate(param_items):
            param_cates.append(content[0])
            comb_cmd.append(" for ")
            comb_cmd.append(param_tokens[idx])
            comb_cmd.append(" in ")
            comb_cmd.append(str(content[1]))

    comb_cmd.append("]")
    comb_cmd = "".join(comb_cmd)

    param_comb_list = eval(comb_cmd)

    return (param_comb_list, param_cates)


(param_comb_list, param_cates) = get_param_comb_list(param_dict)

result_matrix = [[0 for j in y] for i in param_comb_list]

total_p = len(param_comb_list)
count_p = 0
for p_ind, p in enumerate(param_comb_list):

    # fasttext_dir = "/Users/ZhangHaotian/fastText"
    # p = (3, 0.1, 8)
    # param_cates = ["wordNgrams", "lr", "ws"]

    # if param_cates[0] == "preprocess":
    #     pass # add preprocess lines here

    cmd_p = [fasttext_dir, "/fasttext supervised -input data.train.txt -output model"]

    for idx, par in enumerate(param_cates):
        cmd_p.append(" -")
        cmd_p.append(param_cates[idx])
        cmd_p.append(" ")
        cmd_p.append(str(p[idx]))

    cmd_p = "".join(cmd_p)

    kf = KFold(n_splits=10)

    count = 0
    # tempres2 = [0 for i in range(29912)] ###
    for train_index, test_index in kf.split(X_labeled):
        # compose training set based on train_index
        # train_index, test_index = next(kf.split(X_labeled)) ##
        try:
            os.remove("data.train.txt")
        except:
            pass
        with codecs.open("data.train.txt", "a", encoding="utf8") as f:
            for idx in train_index:
                f.write(X_labeled[idx])

        # compose testing set based on test_index
        texts = []
        correct_labels = []
        try:
            os.remove("data.test.txt")
        except:
            pass
        with codecs.open("data.test.txt", "a", encoding="utf8") as f:
            for idx in test_index:
                f.write(X_labeled[idx])
                texts.append(X_unlabeled[idx])
                correct_labels.append(y[idx])

        # compose text used for NDCG
        try:
            os.remove("test.texts.txt")
        except:
            pass
        with codecs.open("test.texts.txt", "a", encoding="utf8") as f:
            for line in texts:
                f.write(line)
                f.write("\n")

        try:
            os.remove(fasttext_dir + "/model.bin")
        except:
            pass
        os.system(cmd_p)

        try:
            os.remove(fasttext_dir + "/lbl.txt")
        except:
            pass
        os.system(fasttext_dir + "/fasttext predict-prob model.bin test.texts.txt " + str(num_labels) + " > lbl.txt")

        with open("lbl.txt") as f:
            index = 0
            for l in f.readlines():
                llist = l.split(" ")
                temp = []
                for eind in range(len(llist) / 2):
                    temp.append((llist[eind * 2][9:], float(llist[eind * 2 + 1])))
                temp = sorted(temp, key=operator.itemgetter(1), reverse=True)
                pred_labels = [it[0] for it in temp]
                corr_labels = correct_labels[index]
                ndcg = ndcg_score(pred_labels, corr_labels)
                result_matrix[p_ind][test_index[index]] = ndcg
                index += 1

    count_p += 1
    with open("track1/" + str(count_p), "w") as fi:
        fi.write("ok")

with open("result_matrix_correct.json", "w") as f: ##need change
    f.write(json.dumps(result_matrix))