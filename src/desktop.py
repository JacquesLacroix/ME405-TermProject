from serial import Serial

def run():
    with Serial('COM5', 9600, timeout=1) as ser:
        while True:
            input("Press Enter to engage gun: ")
            ser.write("Begin\n".encode())
        
            ser.flush()

if __name__ == "__main__":
    run()