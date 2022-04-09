import time


class PSSM:

    # 文件格式转换程序
    def typeChanger(self,formerName, finalName):
        former_file = open(formerName)
        final_file = open(finalName, 'a')
        for line in former_file:
            final_file.write(line)
        former_file.close()
        final_file.close()
        return finalName, formerName

    # 辅助标记程序
    def help_Pro(self,d):
        teq = ['1', ]
        for i in range(len(d)):
            if 'seq-data' in d[i]:
                teq.clear()
            if len(teq) == 0:
                if '}' in d[i]:
                    d[i] = '}12345'
                    return d
                else:
                    continue

    # 提取序列注释程序
    def sequenceComment(self, line):
        t = 0
        comment = ''
        for j in line:
            if j == '"':
                t += 1
            if t == 1:
                comment = comment + j
            else:
                if t == 2:
                    return comment

    # 提取序列编码程序
    def sequenceCode(self, sequence):
        change_str = ''
        for i in sequence:
            i.strip()
            change_str = change_str + i
        t = 0
        outSequence = ''
        for j in change_str:
            if j == '"':
                t += 1
            if t == 1:
                outSequence = outSequence + j
            else:
                if t == 2:
                    return outSequence[1:]

        # 提取PSSM矩阵

    def PSSM_matrix(self, x, pssmBox):
        num = self.d[x + 3:x + 23]
        outLine = ''
        for j in num:
            line = j.replace(',\n', '')
            outLine = outLine + line
        pssmBox.append(outLine)
        if x + 28 <= len(self.d) - 30:
            call = self.PSSM_matrix(x + 28, pssmBox)
        return pssmBox

    # 单行PSSM矩阵重排
    def singlePSSM(self, rowName):
        midBox = []
        pssmLine = ''
        pssmRow = self.pssmBox[rowName].strip()
        midPSSM = pssmRow.replace('        ', ' ')
        midBox = midPSSM.split(' ')
        for j in midBox:  # j代表每行中的元素
            if len(str(j)) == 1:
                # print(j)
                # newNumber = ' ' + j
                newNumber = '' + j
                # pssmLine = pssmLine + '  ' + newNumber
                pssmLine = pssmLine + '' + newNumber
            else:
                # print(j)
                newNumber = j
                # pssmLine = pssmLine + '  ' + newNumber
                pssmLine = pssmLine + '' + newNumber
        return pssmLine

    def __init__(self,fromName, toName):

        print('程序开始运行，请按提示完成操作.\n')
        print('文件格式转换...')

        self.callPro = self.typeChanger(fromName, toName)
        self.formerName = self.callPro[1]
        self.finalName = self.callPro[0]
        # 读取文件
        print('读取文件中...')
        with open(self.formerName, 'r') as u:
            self.d = u.readlines()
            u.close()
        print('读取成功，正在提取PSSM矩阵...')
        # 辅助标记
        self.d = self.help_Pro(self.d)
        # 提取PSSM矩阵
        self.seq = ['1', ]
        self.sequence = ''
        self.yourwant = []
        self.pssmBox = []
        time.sleep(0.2)

    def start(self):
        # global seq
        for line in range(len(self.d)):
            i = self.d[line]
            i.strip()
            if 'title' in i:
                comment = self.sequenceComment()[1:]  # 提取注释
            if 'seq-data' in i:
                self.seq.clear()
                self.seq.append(i)
                self.yourwant.extend(self.seq)
                self.seq.clear()
            if '}12345' in i:
                sequence =self.yourwant[1:]
                self.seq = ['1', ]
                sequence = self.sequenceCode(sequence)  # 提取序列
                sequence = sequence.replace('\n', '')
            else:
                if len(self.seq) == 0:
                    self.yourwant.append(i)
            if 'finalData' in i:
                self.pssmBox = self.PSSM_matrix(line + 2, self.pssmBox)  # 提取PSSM矩阵
        # PSSM矩阵重排显示
        print('提取成功，正在输出文件...')
        Result = ''
        # Result = '>' + comment + '\n' + sequence + '\n'
        # Result = Result + '\n' + 'Last position-specific scoring matrix computed, weighted observed percentages rounded down, information per position, and relative weight of gapless real matches to pseudocounts.\n'
        # Result = Result + '          A   R   N   D   C   Q   E   G   H   I   L   K   M   F   P   S   T   W   Y   V'
        for rowName in range(len(sequence)):
            pssmLine = self.singlePSSM(rowName)  # 重排单行PSSM矩阵  返回1行内的内容
            trueName = rowName + 1
            if len(str(trueName)) == 1:
                rowLine = '  ' + str(trueName)
            else:
                if len(str(trueName)) == 2:
                    rowLine = ' ' + str(trueName)
                else:
                    rowLine = str(trueName)
            # print(rowLine)
            # outRow = rowLine + ' ' + sequence[rowName] + '  ' + pssmLine
            outRow = pssmLine
            # print(outRow)
            Result = Result + '\n' + outRow

        f = open(self.finalName, "w")
        f.write(Result)
        f.close()
        print('PSSM矩阵已成功输出，请查看文件' + self.finalName)