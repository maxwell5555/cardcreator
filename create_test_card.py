from cardcreatorLib import Creator

if __name__ == "__main__":
    creator = Creator("assets/FontA_Cinzel-Bold.otf","assets/FontB_CrimsonPro-VariableFont_wght.ttf","assets/Leyfarer_card_item_Template_v1.png","art/Giants_ring_of_little_folk_Cfallon.png")
    png = creator.generate_card("test", "test", "test", "test", "test") 
    png.save("renders/test.png")