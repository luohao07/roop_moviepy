
def set_false_between(array, min_size):
    pass

if __name__ == '__main__':
    list = [None] * 21
    list[0] = True
    list[5] = False
    list[10] = True
    list[15] = False
    list[20] = False
    set_false_between(list, 7)
    print(list)