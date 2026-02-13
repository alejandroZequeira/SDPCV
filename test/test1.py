from SDPCV import AnalizerYolo

def test_analizer_yolo_init():
    analizer = AnalizerYolo(0)
    analizer.run()
    
if __name__ == "__main__":
    test_analizer_yolo_init()