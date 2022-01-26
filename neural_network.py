from PIL import Image
import random
from random import randint as rand
from sys import exit

# some values
learningRate = 0.5
dataFileName = "datashit.txt"


# sigmoid funk
def sigmoid(x):
    e = 2.71828
    log = e ** x
    return log / (log + 1)


# func save data in file
def saveWeights(saveFileName, size_of_layer, weight):
    data = ''
    for layer in range(len(size_of_layer) - 1):
        for neuron in range(size_of_layer[layer + 1]):
            for synapse in range(size_of_layer[layer]+1):
                data += str(weight[layer][neuron][synapse]) + ';'
            data += '\n'
        data += '\n'
    data += '.'
    file = open(saveFileName, 'w')
    file.write(data)
    file.close()


# setup neur net
def setup(size_of_layer):
    neuron_value = []
    for layer in range(len(size_of_layer)):
        neuron_value.append([])
        for neuron in range(size_of_layer[layer]):
            neuron_value[layer].append(0)
        if layer != len(size_of_layer)-1:
            neuron_value[layer].append(1)  # neuron shift
    return neuron_value


# open file
def getData(size_of_layer):
    weight = []
    try:
        # try to find values
        file = open(dataFileName, 'r')
        for layer in range(len(size_of_layer) - 1):
            weight.append([])
            for neuron in range(size_of_layer[layer + 1]):
                weight[layer].append([])
                for synapse in range(size_of_layer[layer] + 1):
                    value = ''
                    while True:
                        val = file.read(1)
                        if val == ';':
                            break
                        else:
                            value += val
                    value = float(value)
                    weight[layer][neuron].append(value)
        file.close()
        print('get data from file')
    except:
        # arrange weights
        for layer in range(len(size_of_layer) - 1):
            weight.append([])
            for neuron in range(size_of_layer[layer + 1]):
                weight[layer].append([])
                for synapse in range(size_of_layer[layer]+1):
                    weight[layer][neuron].append(random.uniform(-0.1, 0.1))
        print('generate new data')
        saveWeights("datashit.txt", size_of_layer, weight)
    return weight


def convertFile(fileNameIn, fileNameOut, size):
    # open file
    try:
        img = Image.open(fileNameIn)
        trying = False
    except FileNotFoundError:
        return 1

    # crop to norm size
    if img.size[0] > img.size[1]:
        minY = 0
        maxY = img.size[1]
        minX = (img.size[0] - img.size[1]) / 2
        maxX = (img.size[0] - img.size[1]) / 2 + img.size[1]
    elif img.size[0] < img.size[1]:
        minY = (img.size[1] - img.size[0]) / 2
        maxY = (img.size[1] - img.size[0]) / 2 + img.size[0]
        minX = 0
        maxX = img.size[0]
    else:
        minY = 0
        maxY = img.size[1]
        minX = 0
        maxX = img.size[0]

    area = (minX, minY, maxX, maxY)
    img = img.crop(area)
    img = img.resize(size)
    img.save(fileNameOut)
    return 0


def inputLayer(file_name, neuron_value):
    # open file
    trying = True
    while trying:
        try:
            img = Image.open(file_name)
            trying = False
        except FileNotFoundError:
            print("Файл под названием " + file_name + " не найден")
            input("Попробывать снова?")

    # create values
    pixelsRGB = img.load()
    size = [img.size[0], img.size[1]]

    # convert img in values
    pixels = []
    for height in range(size[1]):
        pixels.append([])
        for width in range(size[0]):
            pixelValue = (pixelsRGB[width, height])[0] / 255 / 3 + (pixelsRGB[width, height])[1] / 255 / 3 + \
                         (pixelsRGB[width, height])[2] / 255 / 3
            if pixelValue < 0.1:
                pixelValue = 0.1
            elif pixelValue > 0.9:
                pixelValue = 0.9
            pixels[height].append(pixelValue)
    for height in range(size[0]):
        for width in range(size[1]):
            neuron_value[0][height*size[0] + width] = pixels[height][width]
    return neuron_value


def neural_work(neuron_value, size_of_layer, weight):
    # neuron work
    for layer in range(1, len(size_of_layer)):
        for neuron in range(size_of_layer[layer]):
            neuron_value[layer][neuron] = 0
            for synapse in range(size_of_layer[layer-1] + 1):
                neuron_value[layer][neuron] += neuron_value[layer-1][synapse] * weight[layer-1][neuron][synapse]
            neuron_value[layer][neuron] = sigmoid(neuron_value[layer][neuron])
    return neuron_value


def findAns(outLayer, size_of_layer):
    # find ans
    maxAns = 0
    for ans in range(1, size_of_layer[-1]):
        if outLayer[ans] > outLayer[maxAns]:
            maxAns = ans
    return maxAns


def getAnswer(fileName):
    # open file
    trying = True
    while trying:
        try:
            img = Image.open(fileName)
            trying = False
        except FileNotFoundError:
            print("Файл под названием " + fileName + " не найден")
            input("Попробывать снова?")

    # create values
    pixelsRGB = img.load()
    size = [img.size[0], img.size[1]]

    # convert img in values
    answer = []
    for color in range(3):
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                answer.append(pixelsRGB[x, y][color]/256)
    return answer


def correctWeights(ans, size_of_layer, weight, neuron_value):
    # set true answers for all neurons
    truAnswers = [[]]
    for layer in range(1, len(size_of_layer)):
        truAnswers.append([])
        for neuron in range(size_of_layer[layer]):
            truAnswers[layer].append(0)
        if layer != len(size_of_layer)-1:
            truAnswers[layer].append(0)

    for layer in range(len(size_of_layer)-1, 0, -1):  # from 3 to 0 include
        for neuron in range(size_of_layer[layer] + 1):
            if layer == len(size_of_layer)-1 and neuron == size_of_layer[layer]:
                continue
            elif layer == len(size_of_layer)-1:
                truAnswers[layer][neuron] = ans[neuron] - neuron_value[layer][neuron]
            else:
                for ansNeuron in range(size_of_layer[layer + 1]):
                    truAnswers[layer][neuron] += truAnswers[layer + 1][ansNeuron] * weight[layer][ansNeuron][neuron]

    # correct weights
    # print(truAnswers)
    full_change = 0
    for layer in range(len(size_of_layer) - 1):
        for neuron in range(size_of_layer[layer + 1]):
            for synapse in range(size_of_layer[layer]+1):
                change = truAnswers[layer + 1][neuron] * neuron_value[layer][
                    synapse] * (neuron_value[layer + 1][neuron] * (1 - neuron_value[layer + 1][neuron]))
                weight[layer][neuron][synapse] += change * learningRate
                full_change += abs(change)
    return weight, full_change


def convertImgToBW(fileNameIn, fileNameOut, size):
    # open file
    try:
        img = Image.open(fileNameIn)
        trying = False
    except FileNotFoundError:
        print(fileNameIn)
        return 1

    # crop to norm size
    if img.size[0] > img.size[1]:
        minY = 0
        maxY = img.size[1]
        minX = (img.size[0] - img.size[1]) / 2
        maxX = (img.size[0] - img.size[1]) / 2 + img.size[1]
    elif img.size[0] < img.size[1]:
        minY = (img.size[1] - img.size[0]) / 2
        maxY = (img.size[1] - img.size[0]) / 2 + img.size[0]
        minX = 0
        maxX = img.size[0]
    else:
        minY = 0
        maxY = img.size[1]
        minX = 0
        maxX = img.size[0]

    area = (minX, minY, maxX, maxY)
    img = img.crop(area)
    img = img.resize(size)

    # convert to BW
    pixelsRGB = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            bright = round((pixelsRGB[x, y][0] + pixelsRGB[x, y][1] + pixelsRGB[x, y][2]) / 3)
            brightness = (bright, bright, bright)
            pixelsRGB[x, y] = brightness

    # save
    img.save(fileNameOut)
    return 0


def giveAnsImg(imgPixels, fileName, size):
    # save
    img = Image.new("RGB", size, 0)
    for x in range(size[0]):
        for y in range(size[1]):
            r = round(imgPixels[x+y*size[0]+size[0]*size[0]*0]*256)
            g = round(imgPixels[x+y*size[0]+size[0]*size[0]*1]*256)
            b = round(imgPixels[x+y*size[0]+size[0]*size[0]*2]*256)
            img.paste((r, g, b), (x, y, x+1, y+1))
    img.save(fileName)
    return 0


def main():
    # setup neur net
    imgSize = 24
    size_network = [imgSize * imgSize, imgSize*imgSize*3]
    print(1)
    neuron_value = setup(size_network)
    print(2)
    weight = getData(size_network)
    print(3)
    if weight == 0:
        print("err\nwrong weight")
        exit(1)

    mode = input("0-study\n1-work")
    if mode == '0':
        # study neur net
        tests = 10
        inpImg = "study/img"
        bwImg = "study/BWimg"
        outImg = "study/convertImg"
        for file in range(tests):
            if convertImgToBW(inpImg + str(file) + ".png", bwImg + str(file) + ".png", (imgSize, imgSize)):
                exit("хуятус")
            if convertFile(inpImg + str(file) + ".png", outImg + str(file) + ".png", (imgSize, imgSize)):
                exit(1)
        tackt = 0
        full_change = 0
        maxChange = 100000
        while True:
            num = rand(0, tests - 1)
            neuron_value = inputLayer(bwImg + str(num) + ".png", neuron_value)
            neuron_value = neural_work(neuron_value, size_network, weight)
            ans = getAnswer(outImg + str(num) + ".png")
            weight, change = correctWeights(ans, size_network, weight, neuron_value)
            full_change += change
            tackt += 1
            if tackt == 10:
                saveWeights("datashit.txt", size_network, weight)
                if maxChange > full_change:
                    saveWeights("bestdatashit.txt", size_network, weight)
                    maxChange = full_change
                print(full_change)
                full_change = 0
                tackt = 0
    else:
        # real work neur net
        inpImg = "test/"
        bwImg = "test/BWimg"
        outImg = "test/convertImg"
        while True:
            file = input("file name")
            convertImgToBW(inpImg + str(file) + ".png", bwImg + str(file) + ".png", (imgSize, imgSize))
            neuron_value = inputLayer(bwImg + str(file) + ".png", neuron_value)
            neuron_value = neural_work(neuron_value, size_network, weight)
            giveAnsImg(neuron_value[-1], outImg + str(file) + ".png", (imgSize, imgSize))


if __name__ == "__main__":
    main()
