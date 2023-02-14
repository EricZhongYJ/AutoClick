"""
程序: 自动化可编辑点击模拟器
版本: v0.1
作者: 柯西不等式z
联系方式: qq: 1309352499
请勿抄袭, 如需支持作者, 请通过网盘图片支持作者(也可白嫖)
encoding: utf-8
date: 2023-02-14
"""
# 使用pip install pyautogui下载pyautogui包, tkinter和time包为python自带包无需下载
from pyautogui import moveTo, click, sleep
from tkinter import Tk, Menu, Canvas
from tkinter.messagebox import askyesno as ask
from tkinter.filedialog import askopenfilename as load, asksaveasfilename as save
from time import time


# 初始化
def init():
    global win1, win2, ca, data
    # win1用于启动与提示, 基本设置
    win1.geometry('550x0+700+0')
    win1.resizable(0, 0)
    win1.attributes('-toolwindow', 1)
    win1.attributes('-topmost', 1)  # 窗口顶置
    win1.protocol('WM_DELETE_WINDOW', exit)
    # win1菜单设置
    menu = Menu(win1)
    menu.add_command(label='继续/暂停', command=fun1)
    menu.add_command(label='重新选区', command=fun2)
    menu.add_command(label='打开操作组', command=fun3)
    menu.add_command(label='保存操作组', command=fun4)
    menu.add_command(label='定义新操作组', command=lambda: fun5(1))
    menu.add_command(label='增加操作', command=fun5)
    win1.config(menu=menu)
    # win2用于确定选区, 基本设置
    ca.pack(fill='both')
    win2.attributes('-alpha', 0.3)  # 透明度
    win2.attributes('-fullscreen', 1)  # 窗口最大化
    win2.attributes('-topmost', 1)  # 窗口顶置 todo debug时请注释这一行
    win2.config(cursor='crosshair')
    win2.withdraw()
    # 按键绑定
    win1.bind('<Key>', lambda e: fun1(1))
    win2.bind('<Button-1>', clickDown)  # 左键选区
    win2.bind('<Motion>', clickMove)
    win2.bind('<ButtonRelease-1>', clickUp)
    win2.bind('<Button-3>', clickRight)  # 右键隐藏
    # 启动
    try:
        with open('./default.dat', 'rb') as f:
            rect.extend(int(i) for i in f.read().decode().split(', '))
            f.close()
        if not data[0]:  # 默认使用沙中之火基础数据
            fun3(GROUP_DATA)
    except FileNotFoundError:
        if not ask('提示', '请将窗口[点击模拟器]移动到不遮挡的位置, 点击确定后选择游戏区域'): exit(0)
        win2.deiconify()
    win1.mainloop()


# 按下鼠标
def clickDown(e):
    global mode, rect, timeAt
    if mode < 2:
        rect = [1, e.x, e.y, e.x, e.y]
    elif mode == 2:
        win2.withdraw()
        sleep(0.1)
        click()
        if data[0]:
            data[3].append(int((time() - timeAt) * 100) / 100)
        data[0].append(1)
        data[1].append(e.x)
        data[2].append(e.y)
        timeAt = time()
        # moveTo(1180, 48, 0)  # todo 仅适用up的电脑
        # click()  # todo 仅适用up的电脑
        # moveTo(e.x, e.y, 0)  # todo 仅适用up的电脑


# 移动鼠标
def clickMove(e):
    if mode < 2:
        if rect[0]:
            ca.delete('all')
            if e: rect[3:5] = [e.x, e.y]
            rect[0] = ca.create_rectangle(rect[1], rect[2], rect[3], rect[4], fill='black')


# 松开鼠标
def clickUp(e):
    if mode < 2:
        if rect[0] > 1:
            rect[0] = 0
            if rect[1] > rect[3]: rect[1], rect[3] = rect[3], rect[1]
            if rect[2] > rect[4]: rect[2], rect[4] = rect[4], rect[2]
            win2.attributes('-topmost', 1)  # 顶置窗口
            win2.withdraw()
            with open('./default.dat', 'wb') as f:
                f.write(str(rect[1:])[1:-1].encode())
                f.close()
            if not data[0]:  # 默认使用沙中之火基础数据
                fun3(GROUP_DATA)


# 右键退出
def clickRight(e):
    global at, mode
    win2.withdraw()
    if mode == 2:
        mode = at = 0
        data[3].append(int((time() - timeAt) * 100) / 100)


# 开始/继续
def fun1(pause=None):
    global mode, at
    if mode or pause:
        mode = 0
        win2.withdraw()
    else:
        mode = 1
        try:
            while mode == 1:
                print('当前操作步:', at)
                run()
                at += 1
                if at >= len(data[0]): at = 0
        except KeyboardInterrupt:
            mode = 0
            print('已被用户使用Ctrl+C暂停, 当前操作步:', at)


# 重新选区
def fun2():
    global mode
    mode = 0
    win2.deiconify()


# 打开操作组
def fun3(txt=None):
    global data, at
    if not txt:
        name = load(filetypes=[('数据文件', '.dat .csv'), ('所有类型', '.*')])
        if not name: return
        at = 0  # todo 可设置开始点位置
        with open(name, 'r', encoding='utf-8') as f:
            txt = f.read()
            f.close()
    if ', ' not in txt: txt = txt.replace(',', ', ')
    txt = txt.split('\n')
    _rect = [int(i) for i in txt[0].split(', ')[:4]]
    data = [[int(d) for d in dl.split(', ')] for dl in txt[1:4]]
    data.append([float(d) for d in txt[4].split(', ')])
    for i in range(len(data[0])):
        data[1][i] = round((data[1][i] - _rect[0]) * (rect[3] - rect[1]) / (_rect[2] - _rect[0]) + rect[1])
        data[2][i] = round((data[2][i] - _rect[1]) * (rect[4] - rect[2]) / (_rect[3] - _rect[1]) + rect[2])


# 保存操作组
def fun4():
    name = save(filetypes=[('数据文件', '.dat')])
    if name:
        if not name.endswith('.dat'): name += '.dat'
        with open(name, 'w', encoding='utf-8') as f:
            f.write(str(rect[1:])[1:-1] + '\n')
            f.write(str(data[0])[1:-1] + '\n')
            f.write(str(data[1])[1:-1] + '\n')
            f.write(str(data[2])[1:-1] + '\n')
            f.write(str(data[3])[1:-1])
            f.close()


# 定义新操作组/增加操作
def fun5(n=0):
    global mode, data
    mode = 2
    if n: data = [[], [], [], []]
    win2.deiconify()


# 运行操作组
def run():
    if data[0][at] == 1:
        moveTo(data[1][at], data[2][at], 0.3)
        click()
    elif 999 < data[0][at] < 2000:
        pass  # todo 判断颜色并跳转
    sleep(data[3][at])


if __name__ == '__main__':
    # mode: 0 暂停中, 1 执行操作组, 2 设置操作组
    # at: 当前在第几步
    # rect: 游戏区域 = [mode, x1, y1, x2, y2]
    # data = [[mode], [x], [y], [wait]]
    # data.mode: 0 无, 1 左键单击, todo 2 左键按下, 3 左键松开, 1xxx 判断颜色否则跳转至xxx
    mode = at = timeAt = 0
    win1 = Tk(className='[点击模拟器]-沙中之火挂机')
    win2 = Tk(className='按键绑定')
    ca = Canvas(win2, height=1100, bg='white')
    data = [[], [], [], []]
    rect = [0]
    GROUP_DATA = '''161,82,1759,984
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
1533,1636,1532,1532,1532,229,967,970,1599,1582,1553,1556,251,1466,1541,968,1587,1583,1578,1544,257,1341,1634,1645,1553,1632,220,965,970,1605,1571,1586,1586,256,1488,1459,978,1601,1590,1560,1560,260,1405,1399,1647,1542,1674,201,967,965,1584,1554,1555,1555,257,1426,1522,980,1567,1530,1544,1544,257,1341,1634,1645,1553,1632,220,965,970,1605,1571,1586,1586,256,1488,1459,978,1601,1590,1560,1560,260,1405,1399,1647,1542,1674,201,214,1194,1322,1617,1617,1617
913,145,911,911,911,933,447,408,858,926,651,694,164,638,787,509,871,911,737,726,168,605,872,144,785,140,931,446,408,831,900,737,737,150,606,658,490,852,890,704,704,142,636,633,144,657,104,926,446,421,863,900,714,711,166,625,788,509,845,923,726,726,168,605,872,144,785,140,931,446,408,831,900,737,737,150,606,658,490,852,890,704,704,142,636,633,144,657,104,926,130,911,698,863,863,863
2,1.5,2.5,1.5,4,2,1,0,1,0,0,13,0,6,6,0,1,0,0,13,0,6,6,1,4,1,2,1,0,1,0,0,13,0,6,6,0,1,0,0,13,0,6,6,1,4,1,2,1,0,1,0,0,13,0,6,6,0,1,0,0,13,0,6,6,1,4,1,2,1,0,1,0,0,13,0,6,6,0,1,0,0,13,0,6,6,1,4,1,2,2,1.5,4,1.5,1.5,2.5
'''  # 沙中之火操作数据
    init()
