"""
utils
"""
import heapq
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score


def load_data(fname, irow=5, icol=11, ecol=79, chinese=True):
    """

    @param fname: 数据集文件名，xlsx
    @param irow: 从irow行开始
    @param icol: 从icol列开始
    @param ecol: 从ecol列结束
    @param chinese: 是否为中文数据集
    @return:
    """
    ds = {}
    matrix = []

    df = pd.read_excel(fname)

    # encoding is utf-8 when dealing with Chinese data
    for i in range(irow, len(df.words)):
        word = df.words[i]
        ds[word] = i - irow

        vector = df.iloc[i].iloc[icol:ecol].values
        matrix.append(np.array(vector, dtype=float))

    ds['_matrix_'] = np.around((np.array(matrix)), decimals=4)

    return ds


def load_embeddings(fname, ds_words):
    """
    @param fname: path of word embeddings
    @param ds_words: target words
    @return:
    """
    emb = {}
    matrix = []
    dims = 0
    with open(fname, 'r', encoding='utf-8', errors="ignore") as f:
        for line in f:
            line = line.strip().split()
            if dims == 0:
                if len(line) == 2:
                    continue
                else:
                    dims = len(line) - 1

            word = line[0]
            if word not in ds_words:
                continue

            if word in ['', ' ', '\t', '\n']:
                print('Word {} has no value.'.format(word))
                continue
            try:
                vec = [float(x) for x in line[1:]]
                if len(vec) == dims:
                    arrays = np.array(vec)
                else:
                    continue
            except:
                continue
            if word in emb.keys():
                continue

            emb[word] = len(matrix)  # as indices
            matrix.append(arrays)

    print(len(matrix))
    emb['_matrix_'] = np.array(matrix)  # normalize()

    return emb, dims


def get_vec(word, embs, PRINT_WORD=False):
    """

    @param word:
    @param embs:
    @param PRINT_WORD:
    @return:
    """
    if word in embs.keys():
        try:
            return embs['_matrix_'][embs[word], :]
        except:
            if word != "_matrix_":
                print('{} should have been there but something went wrong when loading it!'.format(word))
            return []
    else:
        if PRINT_WORD:
            print('{} not in the dataset.'.format(word))

        # return np.zeros(embs['_matrix_'][0].shape[0])
        return []


def assign_emb_dataset(ds, ds_words, embs, dim, norm_dim=68):
    """
    @param ds: dataset
    @param ds_words: words
    @param embs:
    @param dim:
    @param norm_dim: size of attributes/ features
    @return:
        X: dataset for training and validation
        Y: labels
        words: words
    """

    words, X, Y = [], [], []
    for i, word in enumerate(ds_words):
        if word not in list(embs.keys()):
            print('Word {} does not appear in embs'.format(word))
            continue
        words.append(word)

        # the second condition needs to be changed for predictions on Dutch norms
        if word in ['domains', '_matrix_']:
            continue

        vec = get_vec(word, embs)
        norm = get_vec(word, ds)

        if len(vec) != dim or len(norm) != norm_dim:
            continue

        X.append(vec)
        Y.append(norm)
    X, Y = np.array(X), np.array(Y)
    return X, Y, words


def return_MSE_by_Feature(Y_test, Y_pred):
    mse = mean_squared_error(Y_test, Y_pred, multioutput='raw_values')
    rmse = np.sqrt(mse)

    return mse, rmse


def return_Spearman_simple(Y_test, Y_pred):
    spear_var = []
    if np.asarray(Y_test).shape != np.asarray(Y_pred).shape:
        assert False, "The size of the prediction array Y and of the test array Y are different."

    Y_pred = np.array(Y_pred)
    Y_test = np.array(Y_test)
    for i in range(len(Y_test[0])):
        var = spearmanr(Y_test[:, i], Y_pred[:, i])[0]
        spear_var.append(var)

    return np.array(spear_var, dtype=float)


def spearman_cof(Y_test, Y_pred):
    """
    @param Y_test: np array
    @param Y_pred: np array
    @return:
    """
    spear_var = []
    if np.asarray(Y_test).shape != np.asarray(Y_pred).shape:
        assert False, "The size of the prediction array Y and of the test array Y are different."

    Y_pred = np.array(Y_pred)
    Y_test = np.array(Y_test)
    for i in range(len(Y_test)):
        var = spearmanr(Y_test[i], Y_pred[i])[0]
        spear_var.append(var)

    return np.array(spear_var, dtype=float)

def return_wf_spearman(Y_test, Y_pred):
    """

    @return: spearman cof across words & features
    """
    sp_w, sp_f = [], []
    Y_pred, Y_test = np.asarray(Y_pred), np.asarray(Y_test)
    if Y_test.shape != Y_pred.shape:
        assert False, "The size of the prediction array Y and of the test array Y are different."

    wn, fn = Y_test.shape
    for i in range(fn):
        var = spearmanr(Y_test[:, i], Y_pred[:, i])[0]
        sp_f.append(var)

    for i in range(wn):
        var = spearmanr(Y_test[i], Y_pred[i])[0]
        sp_w.append(var)

    return np.array(sp_f, dtype=float), np.array(sp_w, dtype=float)








