import sys

DEBUG = True

with open(sys.argv[1]) as f:
    result = list(map(lambda x: x.strip('\n').replace(' ', '').split('<->'), f.readlines()))

result = result[5:] #Cut away initial info

with open(sys.argv[2]) as f:
    actual = {k:v for v,k in map(lambda x: x.strip('\n').replace(' ', '').split('<->'), f.readlines())}

output = open(sys.argv[1][:-4] + '_out.txt', 'w')

def is_match(line):
    return line != 'no_match_found'

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0

for line in result:
    if not is_match(line[0]) and line[1] not in actual:
        if DEBUG:
            print(f'CORRECT (TN): {line[1]} has no match and there is no match in actual', file=output)
        true_negative += 1
    elif line[1] in actual and actual[line[1]] == line[0]:
        if DEBUG:
            print(f'CORRECT (TP): match {line[0]}, {line[1]} is correct', file=output)
        true_positive += 1
    elif is_match(line[0]) and line[1] not in actual:
        if DEBUG:
            print(f'INCORRECT (FP): match {line[0]}, {line[1]} should not be present but is', file=output)
        false_positive += 1
    elif not is_match(line[0]) and line[1] in actual:
        if DEBUG:
            print(f"INCORRECT (FN): match for {line[1]} should be present but isn't", file=output)
        false_negative += 1

print('TP: ', true_positive, file=output)
print('TN: ', true_negative, file=output)
print('FP: ', false_positive, file=output)
print('FN: ', false_negative, file=output)

accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_negative + false_positive)
precision = true_positive / (true_positive + false_positive)
recall = true_positive / (true_positive + false_negative)
print(f"ACCURACY: {accuracy * 100}%", file=output)
print(f"PRECISION: {precision * 100}%", file=output)
print(f"RECALL: {recall * 100}%", file=output)

if(recall != 0 or precision != 0):
    f1 = 2*(recall*precision)/(recall+precision)
    print(f"F1 score: {recall}", file=output)
