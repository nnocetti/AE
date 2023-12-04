import numpy as np
from matplotlib import pyplot as plt

matpvalue=[[0.5029502691915858, 0.9999999999863444, 0.9999999999863444, 0.23213645531080762, 0.9999999999863444, 0.9999999999863444, 0.00040599878758434835, 0.9999999999863444, 0.9999999999863444, 0.9370149034145139, 0.9999999999863444, 0.9999999999863444, 0.06117646292237073, 0.9999999999863444, 0.9999999999863444, 0.024206749732406812, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.5029502691915858, 3.2630699804005627e-07, 1.5099296795810785e-11, 0.11992499559553982, 1.8229457462531186e-08, 1.5099296795810785e-11, 0.11992499559553982, 4.098748614502321e-07, 1.5099296795810785e-11, 0.39222988447477325, 1.3862859725637912e-05, 1.5099296795810785e-11, 0.2746633921339963, 1.0979427662610601e-07, 1.5099296795810785e-11, 0.28461008187076475, 6.797160427710668e-08], [1.5099296795810785e-11, 0.999999697702529, 0.5029502691915858, 1.5099296795810785e-11, 0.9999998372230239, 0.06672704379389652, 1.5099296795810785e-11, 0.9999976277515797, 0.3050037760188406, 1.5099296795810785e-11, 0.99999856051396, 0.9601091764375095, 1.5099296795810785e-11, 0.9999999135295315, 0.27961526789595337, 1.5099296795810785e-11, 0.9999999135295315, 0.2600723060808019], [0.7723515465484312, 0.9999999999863444, 0.9999999999863444, 0.5029502691915858, 0.9999999999863444, 0.9999999999863444, 0.0013121400321819178, 0.9999999999863444, 0.9999999999863444, 0.9722271534328272, 0.9999999999863444, 0.9999999999863444, 0.16642734578636414, 0.9999999999863444, 0.9999999999863444, 0.06483511245414082, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.8830055418594709, 1.7600288130340036e-07, 1.5099296795810785e-11, 0.5029502691915858, 2.546098111742016e-08, 1.5099296795810785e-11, 0.4324968530822437, 2.400534496812863e-07, 1.5099296795810785e-11, 0.7767902820200137, 2.6325044893520866e-05, 1.5099296795810785e-11, 0.6739781887996821, 5.3328388692982216e-08, 1.5099296795810785e-11, 0.6578387066187753, 1.286059087773471e-07], [1.5099296795810785e-11, 0.9999999832402435, 0.9351648875458591, 1.5099296795810785e-11, 0.9999999765718403, 0.5029502691915858, 1.5099296795810785e-11, 0.9999997777976063, 0.8298557674505416, 1.5099296795810785e-11, 0.9999999421672839, 0.9997063133571131, 1.5099296795810785e-11, 0.9999999890263083, 0.9405913277583514, 1.5099296795810785e-11, 0.999999991510237, 0.9021046208244005], [0.9996151355650839, 0.9999999999863444, 0.9999999999863444, 0.9987503038363862, 0.9999999999863444, 0.9999999999863444, 0.5029502691915858, 0.9999999999863444, 0.9999999999863444, 0.9999479671833444, 0.9999999999863444, 0.9999999999863444, 0.9836745304107893, 0.9999999999863444, 0.9999999999863444, 0.9440065639586551, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.8830055418594709, 2.5455867426816834e-06, 1.5099296795810785e-11, 0.5733091316226034, 2.400534496812863e-07, 1.5099296795810785e-11, 0.5029502691915858, 3.141400062542816e-06, 1.5099296795810785e-11, 0.7399276939191981, 0.00036475530503482365, 1.5099296795810785e-11, 0.7351087546869912, 8.031064541499479e-07, 1.5099296795810785e-11, 0.7767902820200137, 2.7310164310611966e-06], [1.5099296795810785e-11, 0.9999996200427316, 0.7001552577438148, 1.5099296795810785e-11, 0.9999997777976063, 0.1739138914879057, 1.5099296795810785e-11, 0.9999970706624237, 0.5029502691915858, 1.5099296795810785e-11, 0.9999991354843688, 0.9874493586353325, 1.5099296795810785e-11, 0.9999998713940912, 0.6020772287667725, 1.5099296795810785e-11, 0.9999998239971187, 0.5616825498430026], [0.06483511245414082, 0.9999999999863444, 0.9999999999863444, 0.02872977301427264, 0.9999999999863444, 0.9999999999863444, 5.528862984041882e-05, 0.9999999999863444, 0.9999999999863444, 0.5029502691915858, 0.9999999999863444, 0.9999999999863444, 0.005381306297705757, 0.9999999999863444, 0.9999999999863444, 0.0014456626525393053, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.6134400287662385, 1.5469453149780893e-06, 1.5099296795810785e-11, 0.2276484534515688, 6.27041960352207e-08, 1.5099296795810785e-11, 0.2648912453130088, 9.304241949218485e-07, 1.5099296795810785e-11, 0.5029502691915858, 7.465775047425945e-05, 1.5099296795810785e-11, 0.36413264799777345, 2.5928375696910844e-07, 1.5099296795810785e-11, 0.43831745015699747, 8.645156312424597e-07], [1.5099296795810785e-11, 0.9999870132000935, 0.04117858544119308, 1.5099296795810785e-11, 0.9999752870009048, 0.00031013268260198586, 1.5099296795810785e-11, 0.9996543741537077, 0.013038738654039338, 1.5099296795810785e-11, 0.9999296656552885, 0.5029502691915858, 1.5099296795810785e-11, 0.9999970706624237, 0.004941700645842906, 1.5099296795810785e-11, 0.9999928508220643, 0.002213596583586509], [0.9405913277583514, 0.9999999999863444, 0.9999999999863444, 0.8372367066104239, 0.9999999999863444, 0.9999999999863444, 0.016937140064760124, 0.9999999999863444, 0.9999999999863444, 0.994842663798831, 0.9999999999863444, 0.9999999999863444, 0.5029502691915858, 0.9999999999863444, 0.9999999999863444, 0.2896471052909906, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.7302448416002976, 9.365489215255814e-08, 1.5099296795810785e-11, 0.3313673790880535, 1.1948693460512103e-08, 1.5099296795810785e-11, 0.2697551583997024, 1.3914370506256117e-07, 1.5099296795810785e-11, 0.641405593196812, 3.141400062542816e-06, 1.5099296795810785e-11, 0.5029502691915858, 2.342815979858047e-08, 1.5099296795810785e-11, 0.5206342545932782, 4.91644527746091e-08], [1.5099296795810785e-11, 0.9999998985852572, 0.7253366078660037, 1.5099296795810785e-11, 0.9999999508355473, 0.06117646292237073, 1.5099296795810785e-11, 0.9999992540979916, 0.4036374753644574, 1.5099296795810785e-11, 0.9999997599465503, 0.9952658651456924, 1.5099296795810785e-11, 0.9999999784469386, 0.5029502691915858, 1.5099296795810785e-11, 0.9999999673613177, 0.3979227712332275], [0.9766220788036141, 0.9999999999863444, 0.9999999999863444, 0.9370149034145139, 0.9999999999863444, 0.9999999999863444, 0.05768117984603142, 0.9999999999863444, 0.9999999999863444, 0.9986225758939726, 0.9999999999863444, 0.9999999999863444, 0.7153899181292352, 0.9999999999863444, 0.9999999999863444, 0.5029502691915858, 0.9999999999863444, 0.9999999999863444], [1.5099296795810785e-11, 0.7203847321040466, 9.365489215255814e-08, 1.5099296795810785e-11, 0.34760769953345494, 9.24997039745644e-09, 1.5099296795810785e-11, 0.2276484534515688, 1.9026314050503836e-07, 1.5099296795810785e-11, 0.5675031469177563, 7.645836962858183e-06, 1.5099296795810785e-11, 0.4852580256501406, 3.54405692721639e-08, 1.5099296795810785e-11, 0.5029502691915858, 8.647046845255718e-08], [1.5099296795810785e-11, 0.9999999372958039, 0.7447010316971777, 1.5099296795810785e-11, 0.9999998811589975, 0.10047444848796416, 1.5099296795810785e-11, 0.9999974544132573, 0.44415142107669436, 1.5099296795810785e-11, 0.9999991968935459, 0.9978870411343107, 1.5099296795810785e-11, 0.9999999546839738, 0.6077701155252268, 1.5099296795810785e-11, 0.999999920179745, 0.5029502691915858]]

matcolor = []
for i, row in enumerate(matpvalue):
    matcolor.append([])
    for j, cell in enumerate(row):
        if i==j:
            matcolor[i].append((1.0,1.0,1.0))
        elif cell < 0.05:
            matcolor[i].append((0.0,1.0,0.0))
        else:
            matcolor[i].append((1.0,0.0,0.0))


fig, ax = plt.subplots(figsize=(10,10))

ax.matshow(matcolor)

for i, row in enumerate(matpvalue):
    for j, cell in enumerate(row):
        ax.text(j, i, f'{cell:.2f}', va='center', ha='center')


# Major ticks
#ax.set_xticks(np.arange(0, 10, 1))
#ax.set_yticks(np.arange(0, 10, 1))

# Labels for major ticks
#ax.set_xticklabels(np.arange(1, 11, 1))
#ax.set_yticklabels(np.arange(1, 11, 1))

plt.yticks([0,1,2,3], ['hola', 'como', 'te', 'va'])

# Minor ticks
ax.set_xticks([x-0.5 for x in range(1,18)], minor=True)
ax.set_yticks([x-0.5 for x in range(1,18)], minor=True)
# Gridlines based on minor ticks
ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
# Remove minor ticks
ax.tick_params(which='minor', top=False, bottom=False, left=False)

plt.tight_layout(pad=0.5)

plt.show()