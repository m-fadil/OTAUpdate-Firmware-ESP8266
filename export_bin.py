import subprocess

def compile_sketch(sketch_path, board_fqbn, output_path):
    try:
        result = subprocess.run([
            "arduino-cli", "compile",
            "--fqbn", board_fqbn,
            "--output-dir", output_path,
            sketch_path
        ], capture_output=True, text=True, check=True)
        print("Sketch compiled successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error: Sketch compilation failed.")
        print("Error message:", e.stderr)

if __name__ == "__main__":
    sketch_path = "./OTAUpdateESP8266"
    board_fqbn = "esp8266:esp8266:nodemcuv2"  # FQBN untuk NodeMCUv2
    output_path = "./build"  # Path untuk menyimpan file biner
    compile_sketch(sketch_path, board_fqbn, output_path)
