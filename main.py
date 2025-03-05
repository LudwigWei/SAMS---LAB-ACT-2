from qr_generator import generate_qr_code

#tester file

# test 1 no data no filename
random_file = generate_qr_code()
print(f"Test 1: Generated random QR code at: {random_file}")

# test 2 
custom_data_file = generate_qr_code(data="Hello perd!")
print(f"Test 2: Generated QR code with custom data at: {custom_data_file}")

# test 3 specific youtube vid with a filename
custom_file = generate_qr_code(data="https://www.youtube.com/watch?v=hLBkxMvAA6Q", filename="lakers_pelicans_03_02_2025")
print(f"Test 3: Generated QR code with custom data and filename at: {custom_file}")

# test 4 multiple random qr
print("\nTest 4: Generating multiple random QR codes...")
for i in range(3):
    file = generate_qr_code()
    print(f"Generated: {file}") 