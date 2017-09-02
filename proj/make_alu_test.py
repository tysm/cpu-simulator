import sys
import shutil

def switch(x):
    return {
        'sll':0,
        'srl':1,
        'add':2,
        'and':3,
        'or':4,
        'xor':5,
        'slt':6,
        'mult':7,
    }.get(x, 8)

user_input = raw_input("Test name: ")
name = user_input
shutil.copyfile("alu-harness.circ", "tests/" + name + ".circ")
f_X = open("tests/"+name+".X", 'w')
f_Y = open("tests/"+name+".Y", 'w')
f_S = open("tests/"+name+".S", 'w')
f_out = open("tests/reference_output/"+name+".out", 'w')
f_X.write("v2.0 raw\n")
f_Y.write("v2.0 raw\n")
f_S.write("v2.0 raw\n")
print("Created files "+name+".X, .Y, and .S in your tests folder, and "+name+".out in your tests/reference_output folder.")
print("For X, Y, Expected Result and Expected Result 2 values, you may enter values in hex, decimal, or binary. Please include approripate prefixes.")
success = 0
#CYCLES
while success==0:
    user_input = raw_input("Number of cycles: ")
    try:
        cycles = int(user_input)
        print(user_input+" cycles")
        success = 1
    except ValueError:
        print("Please enter a valid base-10 number.")
for t in range(cycles):
    success = 0
    #X
    print("You will now enter the values for X and Y in decimal, hex, or binary.\n For example, (245, 0x4080, 0b1010).")
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tX: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                val = int(user_input)
                if val<0:
                    val = 2**16 + val
            s = format(val, '08x')
            f_X.write(s+"\n")
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #Y
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tY: ")
        try:
            if user_input[0:2] == "0x":
                val = int(user_input[2:], 16)
            elif user_input[0:2] == "0b":
                val = int(user_input[2:], 2)
            else:
                val = int(user_input)
                if val<0:
                    val = 2**16 + val
            s = format(val, '08x')
            f_Y.write(s+"\n")
            success = 1
        except ValueError:
            print("Please enter a valid number.")
    success = 0
    #S
    while success==0:
        user_input = raw_input("Time "+str(t)+"\tFunction (e.g add, xor): ")
        if user_input == 'mult':
            result2 = 1
        else:
            result2 = 0
        val = switch(user_input)
        if val != 8:
            s = format(val, '01x')
            f_S.write(s+"\n")
            success = 1
        else:
            print("Please enter valid instruction name. Ex: 'add'")    
    success = 0
    #TIME
    s = format(t, '08b')
    s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
    f_out.write(s+"\t") 
    # #OVERFLOW
    # while success == 0:
    #     user_input = raw_input("Expected Signed Overflow: ")
    #     if user_input == ".":
    #         f_out.write(user_input+"\t")
    #         success = 1
    #     else:
    #         try:
    #             val = int(user_input, 2)
    #             s = format(val, '01b')
    #             f_out.write(s+"\t") 
    #             success = 1
    #         except ValueError:
    #             print("Please enter a '1' or a '0'") 
    # success = 0
    #EQUAL
    while success == 0:
        user_input = raw_input("Expected Equal (enter 0 or 1): ")
        if user_input == ".":
            f_out.write(user_input+"\t")
            success = 1
        else:
            try:
                val = int(user_input, 2)
                s = format(val, '01b')
                f_out.write(s+"\t")
                success = 1
            except ValueError:
                print("Please enter a '1' or a '0'") 
    success = 0
    #RESULT
    while success == 0:
        user_input = raw_input("Expected Result (enter . if it can be anything): ")
        if user_input == ".":
            f_out.write(".... .... .... ....\t")
            success = 1
        else:
            try:
                if user_input[0:2] == "0x":
                    val = int(user_input[2:], 16)
                elif user_input[0:2] == "0b":
                    val = int(user_input[2:], 2)
                else:
                    val = int(user_input)
                    if val<0:
                        val = 2**16 + val
                s = format(val, '016b')
                s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
                f_out.write(s+"\t")
                success = 1
            except ValueError:
                print("Please enter a valid number.")
    #RESULT2
    if result2:
        success = 0
        while success == 0:
            user_input = raw_input("Expected Result2 (enter . if it can be anything): ")
            if user_input == ".":
                f_out.write(".... .... .... ....\n")
                success = 1
            else:
                try:
                    if user_input[0:2] == "0x":
                        val = int(user_input[2:], 16)
                    elif user_input[0:2] == "0b":
                        val = int(user_input[2:], 2)
                    else:
                        val = int(user_input)
                        if val<0:
                            val = 2**16 + val
                    s = format(val, '016b')
                    s = " ".join(s[i:i+4] for i in range(0, len(s), 4))
                    f_out.write(s+"\n")
                    success = 1
                except ValueError:
                    print("Please enter a valid number.")
    else:
        f_out.write(".... .... .... ....\n")
print("Success! Test has been created.")
print("########## INSTRUCTIONS TO RUN THE TEST ###############")
print("'"+name+".circ'. has been added to your 'tests' directory.\n1)Open it, and then load your "+name+".X, .Y and .S files into the corresponding ROM for (X, Y, and switch inputs).\n2) You can do this by probing the ROM, clicking 'Contents' on the sidebar, and then opening the .X/.Y/.S file (then close the window).\n3) Save the .circ file.")
print("4) Add the following line to the list called 'tests' at the end of 'tests/sanity_test_personal.py':")
print("(\""+name+" test\",TestCase(os.path.join(file_locations,'"+name+".circ'), os.path.join(file_locations,'reference_output/"+name+".out'))),") 
f_X.close()
f_Y.close()
f_S.close()
f_out.close() 
