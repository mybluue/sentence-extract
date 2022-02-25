from ltp import LTP
ltp = LTP('base2')
from extract_corpus import *


def extract_construction(test_text):
	text=list()
	text.append(test_text)
	text_list=ltp.sent_split(text)
	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)
	# print(dict(zip([i for i in range(1,len(seg[0])+1)],seg[0])).items())
	# print(dp)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		for triple in text_dp[i]:
			# 动补结构
			if triple[2] == 'CMP':
				# 动量补语
				if id2pos[triple[0]] == 'q':
					dongliang_index = []
					dongliang_index.append(triple[0])
					dongliang_index.append(triple[1])
					for t in text_dp[i]:
						if t[1] == triple[0] and t[2] == 'ATT':
							dongliang_index.append(t[0])
					dongliang_index = sorted(dongliang_index)
					dongliang_index = [i for i in dongliang_index if i >= triple[1]]
					print('\t动量补语',''.join([id2word[i] for i in dongliang_index if id2pos[i] != 'WP']))

				# 时量补语
				elif id2pos[triple[0]] == 'n':
					shiliang_index = []
					shiliang_index.append(triple[0])
					shiliang_index.append(triple[1])
					for t in text_dp[i]:
						if t[1] == triple[0] and id2pos[t[0]] in ['q','m'] and t[2] == 'ATT':
							shiliang_index.append(t[0])
							for l in text_dp[i]:
								if l[1] == t[0] and id2pos[l[0]] == 'm' and l[2] == 'ATT':
									shiliang_index.append(l[0])
					shiliang_index = sorted(shiliang_index)
					shiliang_index = [t for t in shiliang_index if t >= triple[1]]
					print('\t时量补语：',''.join([id2word[i] for i in shiliang_index if id2pos[i] != 'WP']))

				# 可能补语
				if triple[0] - triple[1] == 2 and id2word[triple[1]+1] in ['得','不']:
					print('\t可能补语：',id2word[triple[1]]+id2word[triple[1]+1]+id2word[triple[0]])
				# print('\t动补结构：',id2word[triple[1]]+id2word[triple[0]])
			elif triple[2] == 'DBL':
				jianyuju_index = []
				jianyuju_index.append(triple[0])
				jianyuju_index.append(triple[1])
				for t in text_dp[i]:
					if t[1] == triple[1] and t[0] not in jianyuju_index and t[2] != 'COO':
						jianyuju_index.append(t[0])
				jianyuju_index = sorted(jianyuju_index)
				jianyuju_index = [t for t in jianyuju_index if t >= triple[1]]
				print('\t兼语句：',''.join([id2word[i] for i in jianyuju_index if id2pos[i] != 'wp']))

			elif triple[2] == 'POB' and id2word[triple[1]] == '把':
				baziju_index = []
				baziju_index.append(triple[1])
				target = tail2head[triple[1]]
				baziju_index.append(target)
				baziju_index.append(triple[0])
				for t in text_dp[i]:
					if t[1] == target and t[0] not in baziju_index and t[2] != 'COO':
						baziju_index.append(t[0])
				baziju_index = sorted(baziju_index)
				baziju_index = [t for t in baziju_index if t >= triple[1]]
				print('\t把字句：',''.join([id2word[i] for i in baziju_index if id2pos[i] != 'wp']))

def extract_Subject_Predicate_Phrase_v0(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		for j in range(len(text_dp[i])):
			if text_dp[i][j][2] == 'SBV':
				# 这里是否要添加一个中间有标点符号的判断并跳过
				has_something_after_SBV = False
				subject_predicate_phrase = ''
				SBV_span = ''.join([id2word[t] for t in range(text_dp[i][j][0],text_dp[i][j][1])])
				subject_predicate_phrase += SBV_span
				for k in range(j+1,len(text_dp[i])):
					if text_dp[i][k][1] == text_dp[i][j][1]:
						if text_dp[i][k][2] == 'VOB':
							has_something_after_SBV = True
							VOB_span = ''.join([id2word[t] for t in range(text_dp[i][j][1],text_dp[i][k][0]+1)])
							subject_predicate_phrase += VOB_span
						elif text_dp[i][k][2] == 'CMP':
							has_something_after_SBV = True
							has_something_after_CMP = False
							CMP_span = ''.join([id2word[t] for t in range(text_dp[i][j][1],text_dp[i][k][0])])
							subject_predicate_phrase += CMP_span
							for l in range(len(text_dp[i])-1,k,-1):
								# ③ SBV - CMP - complememt
								if text_dp[i][l][1] == text_dp[i][k][0]:
									has_something_after_CMP = True
									complement_span = ''.join([id2word[t] for t in range(text_dp[i][k][0],text_dp[i][l][0]+1)])
									subject_predicate_phrase += complement_span
									break
								# ② SBV - CMP
							if not has_something_after_CMP:
								subject_predicate_phrase += id2word[text_dp[i][k][0]]

						elif text_dp[i][k][2] == 'RAD' and id2word[text_dp[i][k][0]] not in ['的']:
							has_something_after_SBV = True
							has_something_after_RAD = False
							RAD_span = ''.join([id2word[t] for t in range(text_dp[i][j][1],text_dp[i][k][0]+1)])
							subject_predicate_phrase += RAD_span
				# ⑥ SBV
				if not has_something_after_SBV:
					subject_predicate_phrase += id2word[text_dp[i][j][1]]
						
				print('\t主谓：',subject_predicate_phrase)


def extract_Subject_Predicate_Phrase(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		for j in range(len(text_dp[i])):
			if text_dp[i][j][2] == 'SBV':
				# 这里是否要添加一个中间有标点符号的判断并跳过
				subject_predicate_span = set()
				# 加上修饰主语的ATT成分
				for k in range(0,j):
					if text_dp[i][k][1] == text_dp[i][j][0] and text_dp[i][k][2] == 'ATT':
						ATT_subject_span = [t for t in range(text_dp[i][k][0],text_dp[i][k][1])]
						subject_predicate_span.update(set(ATT_subject_span))

				has_something_after_SBV = False
				
				SBV_span = [t for t in range(text_dp[i][j][0],text_dp[i][j][1]+1)]
				subject_predicate_span.update(set(SBV_span))
				for k in range(j+1,len(text_dp[i])):
					if text_dp[i][k][1] == text_dp[i][j][1]:
						if text_dp[i][k][2] == 'VOB':
							has_something_after_SBV = True
							VOB_span = [t for t in range(text_dp[i][j][1],text_dp[i][k][0]+1)]
							subject_predicate_span.update(set(VOB_span))
							# 加上VOB短语的COO短语
							for l in range(len(text_dp[i])-1,k,-1):
								if text_dp[i][l][1] == text_dp[i][k][1] and text_dp[i][l][2] == 'COO':
									VOB_COO_span = [t for t in range(text_dp[i][l][1], text_dp[i][l][0]+1)]
									subject_predicate_span.update(set(VOB_COO_span))
									for m in range(len(text_dp[i])-1, l, -1):
										if text_dp[i][m][1] == text_dp[i][l][0] and text_dp[i][m][2] == 'VOB':
											COO_VOB_span = [t for t in range(text_dp[i][m][1], text_dp[i][m][0]+1)]
											subject_predicate_span.update(set(COO_VOB_span))
											break
									break

							
						elif text_dp[i][k][2] == 'CMP':
							has_something_after_SBV = True
							has_something_after_CMP = False
							CMP_span = [t for t in range(text_dp[i][j][1],text_dp[i][k][0]+1)]
							subject_predicate_span.update(CMP_span)
							for l in range(len(text_dp[i])-1,k,-1):
								# ③ SBV - CMP - complememt
								if text_dp[i][l][1] == text_dp[i][k][0]:
									has_something_after_CMP = True
									complement_span = [t for t in range(text_dp[i][k][0],text_dp[i][l][0]+1)]
									subject_predicate_span.update(set(complement_span))
									break
							# ② SBV - CMP
							if not has_something_after_CMP:
								pass

							# 加上动补短语的COO短语
							for l in range(len(text_dp[i])-1,k,-1):
								if text_dp[i][l][1] == text_dp[i][k][1] and text_dp[i][l][2] == 'COO':
									CMP_COO_span = [t for t in range(text_dp[i][l][1], text_dp[i][l][0]+1)]
									subject_predicate_span.update(set(CMP_COO_span))
									for m in range(len(text_dp[i])-1, l, -1):
										if text_dp[i][m][1] == text_dp[i][l][0] and text_dp[i][m][2] == 'VOB':
											COO_VOB_span = [t for t in range(text_dp[i][m][1], text_dp[i][m][0]+1)]
											subject_predicate_span.update(set(COO_VOB_span))
											break
									break

						elif text_dp[i][k][2] == 'RAD' and id2word[text_dp[i][k][0]] not in ['的']:
							has_something_after_SBV = True
							has_something_after_RAD = False
							RAD_span = [t for t in range(text_dp[i][j][1],text_dp[i][k][0]+1)]
							subject_predicate_span.update(set(RAD_span))
							for l in range(len(text_dp[i])-1,k,-1):
								# ⑤ SBV - RAD - object
								if text_dp[i][l][1] == text_dp[i][j][1] and id2pos[text_dp[i][l][0]] != 'wp':
									has_something_after_RAD = True
									obj_span = [t for t in range(text_dp[i][j][1],text_dp[i][l][0]+1)]
									subject_predicate_span.update(set(obj_span))
									break
							# ④ SBV - RAD
							if not has_something_after_RAD:
								pass
				# ⑥ SBV
				if not has_something_after_SBV:
					pass
				subject_predicate_phrase = ''.join([id2word[t] for t in sorted(list(subject_predicate_span))])
						
				print('\t主谓：',subject_predicate_phrase)

# extract_Subject_Predicate_Phrase(subject_predicate)
# exit()

def extract_Verb_Object_Phrase(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		all_verb_object_span = list()
		for j in range(len(text_dp[i])):
			if text_dp[i][j][2] == 'VOB':
				verb_object_span = set()
				VOB_span = [t for t in range(text_dp[i][j][1],text_dp[i][j][0]+1)]
				
				wp_index = [t for t in VOB_span if id2word[t] in [',','.','。','!','?',':','：','，']]
				if not wp_index:
					verb_object_span.update(set(VOB_span))

				# 将两个连在一起的VOB短语合在一起
				# for k in range(len(text_dp[i])-1, j, -1):
				# 	if text_dp[i][k][1] == text_dp[i][j][0] and text_dp[i][k][2] == 'VOB':
				# 		adjacent_VOB_span = [t for t in range(text_dp[i][k][1], text_dp[i][k][0]+1)]
				# 		wp_index = [t for t in adjacent_VOB_span if id2word[t] in [',','.','。','!','?',':','：']]
				# 		if not wp_index:
				# 			verb_object_span.update(set(adjacent_VOB_span))

				if verb_object_span:
					# verb_object_phrase = ''.join([id2word[t] for t in sorted(list(verb_object_span))])
					# print('\t动宾短语：',verb_object_phrase)
					all_verb_object_span.append(verb_object_span)
		union_verb_object_span = list()
		all_verb_object_span = [sorted(list(span)) for span in all_verb_object_span]
		all_verb_object_span = sorted(all_verb_object_span, key= lambda x:x[0])
		# 去除重叠子短语
		all_verb_object_span_no_repeat = list()
		for span in all_verb_object_span:
			if not all_verb_object_span_no_repeat:
				all_verb_object_span_no_repeat.append(span)
			else:
				no_repeat = True
				for t in all_verb_object_span_no_repeat:
					if span[0] >= t[0] and span[-1] <= t[-1]:
						no_repeat = False
						break
				if no_repeat:
					all_verb_object_span_no_repeat.append(span)

		# print(all_verb_object_span_no_repeat)
		for vb_span in all_verb_object_span_no_repeat:
			if not union_verb_object_span or union_verb_object_span[-1][-1] != vb_span[0]:
				union_verb_object_span.append(vb_span)
			else:
				union_verb_object_span[-1] += vb_span
				union_verb_object_span[-1] = sorted(list(set(union_verb_object_span[-1])))

		# print(union_verb_object_span)
		for vb_span in union_verb_object_span:
			print('\t动宾短语：',''.join([id2word[t] for t in vb_span]))

# extract_Verb_Object_Phrase(text1+text2+text3+subject_predicate)
# extract_Verb_Object_Phrase("母亲知道那是我在安慰她而已。")
# extract_Verb_Object_Phrase("这是一种比海棠大不了多少的小果子，居然每个都长着疤，有的还烂了皮，只是让母亲一一剜去了疤，洗得干干净净。")
# exit()

def extract_Endocentric_Phrase(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		all_ATT_span, all_ADV_span = [], []
		for j in range(len(text_dp[i])):
			# 定中短语
			if text_dp[i][j][2] == 'ATT' and id2pos[text_dp[i][j][0]] not in ['q']:
				ATT_span = set()
				ATT_span.update(set([t for t in range(text_dp[i][j][0],text_dp[i][j][1]+1)]))
				for k in range(j+1,len(text_dp[i])):
					if text_dp[i][k][0] == text_dp[i][j][1] and text_dp[i][k][2] == 'ATT':
						ATT_span.update(set([t for t in range(text_dp[i][k][0],text_dp[i][k][1]+1)]))
				all_ATT_span.append(ATT_span)
				# endocentric_phrase = ''.join([id2word[t] for t in sorted(list(ATT_span))])
				# print('\t定中短语:',endocentric_phrase)

			# 状中短语
			elif text_dp[i][j][2] == 'ADV':
				ADV_span = set()
				ADV_span.update(set([t for t in range(text_dp[i][j][0],text_dp[i][j][1]+1)]))
				for k in range(0,j):
					if text_dp[i][k][1] == text_dp[i][j][0] and text_dp[i][k][2] == 'ATT':
						ADV_span.update(set([t for t in range(text_dp[i][k][0],text_dp[i][k][1]+1)]))

				# 状语和中心语之间不能有标点符号
				wp_index = [t for t in ADV_span if id2word[t] in [',','.','。','!','?',':','：','，']]
				if not wp_index:
					all_ADV_span.append(ADV_span)
				# endocentric_phrase = ''.join([id2word[t] for t in list(ADV_span)])
				# print('\t状中短语：',endocentric_phrase)
		# 去除重叠子短语
		all_ATT_span = [sorted(list(t)) for t in all_ATT_span]
		all_ADV_span = [sorted(list(t)) for t in all_ADV_span]
		all_ATT_span = sorted(all_ATT_span, key=lambda x:x[0])
		all_ADV_span = sorted(all_ADV_span, key=lambda x:x[0])

		all_ATT_span_no_repeat = list()

		for x in all_ATT_span:
			if not all_ATT_span_no_repeat:
				all_ATT_span_no_repeat.append(x)
			else:
				no_repeat = True
				for y in all_ATT_span_no_repeat:
					if x[0] >= y[0] and x[-1] <= y[-1]:
						no_repeat = False
						break
				if no_repeat:
					all_ATT_span_no_repeat.append(x)

		all_ADV_span_no_repeat = list()

		for x in all_ADV_span:
			if not all_ADV_span_no_repeat:
				all_ADV_span_no_repeat.append(x)
			else:
				no_repeat = True
				for y in all_ADV_span_no_repeat:
					if x[0] >= y[0] and x[-1] <= y[-1]:
						no_repeat = False
						break
				if no_repeat:
					all_ADV_span_no_repeat.append(x)

		for att_span in all_ATT_span_no_repeat:
			print('\t定中短语：',''.join([id2word[t] for t in att_span]))

		for adv_span in all_ADV_span_no_repeat:
			print('\t状中短语：',''.join([id2word[t] for t in adv_span]))



# extract_Endocentric_Phrase(endocentric_dingzhong+endocentric_zhuangzhong)
# extract_Endocentric_Phrase(endocentric_dingzhong + endocentric_zhuangzhong + coordinate_phrase1 + coordinate_phrase2)
# exit()

def extract_Verb_Complement_Phrase(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		has_CMP = False
		for j in range(len(text_dp[i])):
			if text_dp[i][j][2] == 'CMP':
				has_CMP = True
				verb_complement_span = set()
				CMP_span = [t for t in range(text_dp[i][j][1],text_dp[i][j][0]+1)]
				verb_complement_span.update(set(CMP_span))

				for k in range(len(text_dp[i])-1,j,-1):
					if text_dp[i][k][1] == text_dp[i][j][0] and text_dp[i][k][2] in ['RAD','POB','COO','VOB']:
						something_after_span = [t for t in range(text_dp[i][k][1],text_dp[i][k][0]+1)]
						verb_complement_span.update(set(something_after_span))
				verb_complement_phrase = ''.join([id2word[t] for t in sorted(list(verb_complement_span))])
				print('\t动补短语：',verb_complement_phrase)
		if not has_CMP:
			for j in range(len(text_dp[i])):
				if id2pos[text_dp[i][j][0]] == 'v' and id2pos[text_dp[i][j][0]+1] == 'm' and id2pos[text_dp[i][j][0]+2] == 'q':
					verb_complement_phrase = id2word[text_dp[i][j][0]] + id2word[text_dp[i][j][0]+1] + id2word[text_dp[i][j][0]+2]
					if id2pos[text_dp[i][j][0]+3] == 'n':
						verb_complement_phrase += id2word[text_dp[i][j][0]+3]
					print('\t动补短语：',verb_complement_phrase)

# extract_Verb_Complement_Phrase(verb_complement)


# from collections import deque
def extract_Coordinate_Phrase(input_text,is_sent_splited=False):
	if is_sent_splited:
		text_list = input_text
	else:
		text = list()
		text.append(input_text)
		text_list = ltp.sent_split(text)

	text_seg,hidden=ltp.seg(text_list)
	text_pos = ltp.pos(hidden)
	text_dp = ltp.dep(hidden)

	for i in range(len(text_dp)):
		id2word = dict(zip([t for t in range(1,len(text_seg[i])+1)],text_seg[i]))
		id2pos = dict(zip([t for t in range(1,len(text_pos[i])+1)],text_pos[i]))
		tail2head = {t[0]:t[1] for t in text_dp[i]}
		print('当前句子：',''.join(text_seg[i]))
		COO_span_stack = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
		top = -1
		for j in range(len(text_dp[i])):
			if text_dp[i][j][2] == 'COO':
				# 栈空
				if top == -1:
					top += 1
					COO_span_stack[top] = [text_dp[i][j][1],text_dp[i][j][0]]
					continue
				# print(top, COO_span_stack[top], [text_dp[i][j][1],text_dp[i][j][0]])

				while top >= 0 and text_dp[i][j][1] <= COO_span_stack[top][0]:
					top -= 1
					# print(top)
				top += 1
				COO_span_stack[top] = [text_dp[i][j][1],text_dp[i][j][0]]

				# 查看新的栈顶元素[text_dp[i][j][1],text_dp[i][j][0]]是否能和下面的元素合并
				top -= 1
				need_merge_span = []
				while top>=0 and text_dp[i][j][1] > COO_span_stack[top][0] and text_dp[i][j][1] <= COO_span_stack[top][1]:
					need_merge_span = COO_span_stack[top]
					top -= 1
				top += 1
				if need_merge_span:
					COO_span_stack[top] = [need_merge_span[0],text_dp[i][j][0]]
				
		for st in range(top+1):
			coordinate_span = COO_span_stack[st]
			# 添加第一个并列结构前的修饰成分
			for l in range(coordinate_span[0]):
				if text_dp[i][l][1] == coordinate_span[0]:
					if text_dp[i][l][2] in ['ATT','ADV'] :
						coordinate_span[0] = text_dp[i][l][0]
						break
			# 如果右侧的并列成分是动词，添加它的宾语;未考虑宾语是个并列短语
			if id2pos[coordinate_span[1]] == 'v':
				# coordinate_span[1]对应的下标是coordinate_span[1]-1
				for l in range(len(text_dp[i])-1,coordinate_span[1]-1,-1):
					if text_dp[i][l][1] == coordinate_span[1] and text_dp[i][l][2] in ['VOB']:
						coordinate_span[1] = text_dp[i][l][0]
						break

			coordinate_phrase = ''.join([id2word[t] for t in range(coordinate_span[0],coordinate_span[1]+1)])
			print('\t联合短语：',coordinate_phrase)



# extract_Subject_Predicate_Phrase(subject_predicate + coordinate_phrase1 + coordinate_phrase2)
# extract_Coordinate_Phrase('他的面部表情、身体动作，他的内心激动，还有成功，都以夸大力度表现出来了。')

# extract_Endocentric_Phrase(endocentric_dingzhong + endocentric_zhuangzhong + coordinate_phrase1 + coordinate_phrase2)

# extract_Verb_Object_Phrase(verb_object + coordinate_phrase1 + coordinate_phrase2)


test_text = '对我影响最大的一个人，那就是我姥姥。姥姥过世已将近有十年了。我对她的认识是早在我刚上幼儿园时开始的。当时我是一个极内向、怕生人的孩子，说什么话、做什么事老缠着妈妈转转 ，她一离开我，我非要马上大哭一通 。妈妈肚子里有了我妹妹之后，因为她有很严重的反应，吃不下东西睡不好觉，体质一天比一天弱了。姥姥听了这个消息之后，马上赶到我家照料妈妈，料理家里的一切事情。我还依稀地记得姥姥到家的那一天。当时，我和平时一样总不肯离开妈妈的身边，姥姥满脸笑容地一直看着我，并没有说什么像你乖乖，姥姥给你好吃的等等迎合孩子的恭维话，而是一直笑眯眯地看着我。那种神态却给了我一种安慰感，靠小孩子的直觉，这个人不会是坏人。 姥姥在家的那半年，我还是 终于没有跟她打心眼里说到一起去玩到一起去，但是她给我留下了不可思议的很神秘的印象。 后来，随着我长大成人，妈妈不知多少次跟我讲过姥姥的故事啊！ 姥姥是个乡下人，为了维持生活，她每天到地里跟男人们一起干活种田。晚上她连饭都没来得及吃好就喂蚕桑叶从中提出丝来，然后给五个孩子做很漂亮的和服穿。此外，洗衣服和各种家务活都是由她一个人承担的。而姥姥的口头话总是那么一句：“我这么笨，还得好好干呀！”姥姥的形象不知不觉地给了我一种潜移默化的教育，到现在我对姥姥的伟大觉得不可估量的精神力量 。'
extract_Coordinate_Phrase(test_text)