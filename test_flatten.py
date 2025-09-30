def flatten_list(mylist):
    list_n = []
    for num in mylist:
        if type(num) == type([]):
            list_n.extend(flatten_list(num))
        else:
            list_n.append(num)
    return list_n

print(flatten_list(['1', ['4', ['5', ['3']], '2'], '9']))

