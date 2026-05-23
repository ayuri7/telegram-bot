a1, b1, a2, b2 = int(input()), int(input()), int(input()), int(input())
if b1 < b2:
    if b1 == a2:
        print(a2)
        if a1 > a2:
            print(a1, b1)
            if a1 == a2:
                print(a1, b1)
                if a1 < a2:
                    print(a2, b1)
                else:
                     print( "пустое множество" )
elif b1 > b2:
    if a2 == b1:
        print( a2 )
        if a1 < a2:
            print( a2, b1 )
            if a1 == a2:
                print( a2, b1)
                if a1 > a2:
                    print( a1, b1)
                else:
                     print( "пустое множество" )
elif b1 == b2:
    if a1 > a2:
        print( a1, b1)
        if a1 < a2:
            print( a2, b2)
            if a1 == a2:
                print( a1, b1 )
            else:
               print( "пустое множество" )
