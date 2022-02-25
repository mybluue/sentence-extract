from ltp import LTP
ltp = LTP('base2')

def extract_completement(input_text,pre_sent_split = False):
    if not pre_sent_split:
        text = list()
        text.append(input_text)
        text_list = ltp.sent_split(text)
    else:
        text_list = input_text

    text_seg, hidden = ltp.seg(text_list)
    text_pos = ltp.pos(hidden)
    text_dp = ltp.dep(hidden)
    label_list = []

    for i in range(len(text_dp)):
        id2word = dict(zip([t for t in range(1, len(text_seg[i]) + 1)], text_seg[i]))
        id2pos = dict(zip([t for t in range(1, len(text_pos[i]) + 1)], text_pos[i]))
        sent = ''.join(text_seg[i])
        label = ''
        for triple in text_dp[i]:
            if triple[2] == 'CMP':  # 动补结构
                # 动量补语
                if id2pos[triple[0]] == 'q':
                    if id2word[triple[0]] in ['年', '天', '月', '日']:
                        label = '时量补语'
                    else:
                        label = '动量补语'
                # 时量补语
                elif id2pos[triple[0]] == 'n':
                    label = '时量补语'
                # 可能补语
                elif triple[0] - triple[1] == 2 and id2word[triple[1] + 1] in ['得', '不']:
                    label = '可能补语'
        label_list.append([sent, label])
    return label_list


def extract_2objlink(input_text,pre_sent_split = False):
    if not pre_sent_split:
        text = list()
        text.append(input_text)
        text_list = ltp.sent_split(text)
    else:
        text_list = input_text

    text_seg, hidden = ltp.seg(text_list)
    text_pos = ltp.pos(hidden)
    text_dp = ltp.dep(hidden)
    label_list = []

    for i in range(len(text_dp)):
        id2word = dict(zip([t for t in range(1, len(text_seg[i]) + 1)], text_seg[i]))
        id2pos = dict(zip([t for t in range(1, len(text_pos[i]) + 1)], text_pos[i]))
        sent = ''.join(text_seg[i])
        label = ''
        for triple in text_dp[i]:
            if triple[2] == 'DBL':  # 兼语句
                label = '兼语句'
        label_list.append([sent, label])
    return label_list


def extract_sentba(input_text, pre_sent_split = False):
    if not pre_sent_split:
        text = list()
        text.append(input_text)
        text_list = ltp.sent_split(text)
    else:
        text_list = input_text

    text_seg, hidden = ltp.seg(text_list)
    text_pos = ltp.pos(hidden)
    text_dp = ltp.dep(hidden)
    label_list = []

    for i in range(len(text_dp)):
        id2word = dict(zip([t for t in range(1, len(text_seg[i]) + 1)], text_seg[i]))
        id2pos = dict(zip([t for t in range(1, len(text_pos[i]) + 1)], text_pos[i]))
        sent = ''.join(text_seg[i])
        label = ''
        for triple in text_dp[i]:
            if triple[2] == 'POB' and id2word[triple[1]] == '把':  # 把字句
                label = '把字句'
        label_list.append([sent, label])
    return label_list
text = '你把电视关了吧，咱们说会儿话。她的儿女都已经长大成人了，各自忙着自己的事情，匆匆回去看她一下，就匆匆离去。办公室在三楼，我们上楼去，先把借书证办了。真对不起，我把这事儿忘了。你把电视关了吧。我们收到礼物就马上把它打开。工作累的时候，我就到外面去浇浇花，把这些盆景修整修整。我让她中午再给你打。'
# print(extract_sentba(text))

# exit()
import xlrd

data = xlrd.open_workbook('结构抽取测评语料.xlsx')
sheet = data.sheets()[4]

text = sheet.col_values(0)[1:]
label = sheet.col_values(1)[1:]
label = [l.split(',') for l in label]
complement_res = extract_completement(text,pre_sent_split=True)
jianyu_res = extract_2objlink(text, pre_sent_split=True)
baziju_res = extract_sentba(text, pre_sent_split=True)

# 计算预测的准确率和召回率

def staticPC(label, predict, target):
    TP, FP, TN, FN = 0, 0, 0, 0
    target_cnt = len([l for l in label if target in l])
    for i in range(len(predict)):
        # 真正
        if target in label[i] and predict[i][1] == target:
            TP += 1
        # 假正
        elif predict[i][1] == target and target not in label[i]:
            FP += 1
        # 真错
        elif predict[i][1] != target and target not in label[i]:
            TN += 1
        # 假错
        elif predict[i][1] != target and target in label[i]:
            FN += 1
            # 打印没召回的数据
                # print(predict[i],target)
        else:
            pass

        
    precison = TP / (TP + FP)
    recall = TP / (TP + FN)
    return precison,recall

print(staticPC(label, complement_res, '时量补语'))
# exit()
print(staticPC(label, complement_res, '动量补语'))
print(staticPC(label, complement_res, '可能补语'))
print(staticPC(label, jianyu_res, '兼语句'))
print(staticPC(label, baziju_res, '把字句'))



