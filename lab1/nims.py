stones = 100

while stones > 0:
    print("There are {} stones left".format(stones))
    numberAccepted = False
    while not numberAccepted:
        num = input("How many stones would you like to pick up: ")
    
        if num.isnumeric():
            num = int(num)
            if num > 0 and num <= 5:
                if (stones - num < 0):
                    print("You can not take this many stones")
                else:
                    stones = stones - num
                    numberAccepted = True
                    
                    if (stones == 0):
                        print("You win")
                    else:
                        print("There are {} stones left".format(stones))
            else:
                print("You can not take this many stones")
        else:
            print("Please input a number")
    
    if stones > 10:
        stones = stones - 5
        print("The enemy takes 5 stones")
    elif stones == 6:
        stones = stones - 5
        print("The enemy takes 5 stones")
    elif stones > 5:
        val = stones - 6
        stones = stones - val
        print("The enemy takes {} stones".format(val))
    elif stones > 0:
        val = stones
        stones = stones - val
        print("The enemy takes {} stones".format(val))
        print("The enemy wins")
