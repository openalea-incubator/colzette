from openalea.colzette import Colzette

if __name__ == '__main__':
    # Showcase Colzette inspection
    for p in Colzette.parameters():
        print(f"{p.name}: {p.metadata['description']}, default value = {p.default:.3e}")
    instance = Colzette(density=32, coeff_width_leaf_brassica=0.4)
    instance.run()
    print(instance.agg["Eabs"])

