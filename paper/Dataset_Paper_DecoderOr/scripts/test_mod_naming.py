import subprocess

names = ['\\3bit_Comparator_Decoder_OR ', '_3bit_Comparator_Decoder_OR', 'mod_3bit_Comparator_Decoder_OR']
for name in names:
    code = f'module {name} (input wire A, output wire Y); assign Y = A; endmodule\n'
    Path = '/tmp/t.v'
    subprocess.run(['wsl', '-e', 'bash', '-c', f'cat > {Path} << "EOF"\n{code}EOF'], check=True)
    res_iv = subprocess.run(['wsl', '-e', 'bash', '-c', f'iverilog {Path} -o /tmp/t.vvp'], capture_output=True, text=True)
    res_ys = subprocess.run(['wsl', '-e', 'bash', '-c', f'yosys -p "read_verilog {Path}"'], capture_output=True, text=True)
    res_vl = subprocess.run(['wsl', '-e', 'bash', '-c', f'verilator --lint-only -Wall -Wno-DECLFILENAME {Path}'], capture_output=True, text=True)
    print(f'{name}: iv={res_iv.returncode}, ys={res_ys.returncode}, vl={res_vl.returncode}')
