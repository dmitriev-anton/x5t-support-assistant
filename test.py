sales = {}
while True:
    c, p, q = input().split()
    q = int(q)
    sales[c][p]= sales.get(c,{}).get(p, 0)
    print(sales.get(c,{}).get(p, 0))
    print(sales)