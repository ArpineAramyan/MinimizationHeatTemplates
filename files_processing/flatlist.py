def flatlist(l, output):
    for i in l:
        if type(i) == list:
            flatlist(i, output)
        else:
            output.append(i)