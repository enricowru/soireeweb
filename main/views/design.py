from django.shortcuts import render

def moredesign(request):
    sets = {
        'themed_backdrop': [
            {
                'title': 'Sanrio: Hello Kitty and Friends',
                'images': [
                    'images/upgraded balloon set-up/R1C.jpg',
                    'images/upgraded balloon set-up/R1A.jpg',
                    'images/upgraded balloon set-up/R1D.jpg',
                    'images/upgraded balloon set-up/R1B.jpg',
                ]
            },
            {
                'title': 'Teddy Bear',
                'images': [
                    'images/upgraded balloon set-up/R2C.jpg',
                    'images/upgraded balloon set-up/R2A.jpg',
                    'images/upgraded balloon set-up/R2D.jpg',
                    'images/upgraded balloon set-up/R2B.jpg',
                ]
            },
            {
                'title': 'Kuromi and My Melody (2)',
                'images': [
                    'images/upgraded balloon set-up/R3C.jpg',
                    'images/upgraded balloon set-up/R3A.jpg',
                    'images/upgraded balloon set-up/R3D.jpg',
                    'images/upgraded balloon set-up/R3B.jpg',
                ]
            },
            {
                'title': 'Baby Blue Bear',
                'images': [
                    'images/upgraded balloon set-up/R4C.jpg',
                    'images/upgraded balloon set-up/R4A.jpg',
                    'images/upgraded balloon set-up/R4D.jpg',
                    'images/upgraded balloon set-up/R4B.jpg',
                ]
            },
            {
                'title': 'Disney Princesses',
                'images': [
                    'images/upgraded balloon set-up/R5C.jpg',
                    'images/upgraded balloon set-up/R5A.jpg',
                    'images/upgraded balloon set-up/R5D.jpg',
                    'images/upgraded balloon set-up/R5B.jpg',
                ]
            },
            {
                'title': 'Safari Jungle',
                'images': [
                    'images/upgraded balloon set-up/R6C.jpg',
                    'images/upgraded balloon set-up/R6A.jpg',
                    'images/upgraded balloon set-up/R6D.jpg',
                    'images/upgraded balloon set-up/R6B.jpg',
                ]
            },
            {
                'title': 'Iron Man and Frozen',
                'images': [
                    'images/upgraded balloon set-up/R7C.jpg',
                    'images/upgraded balloon set-up/R7A.jpg',
                    'images/upgraded balloon set-up/R7D.jpg',
                    'images/upgraded balloon set-up/R7B.jpg',
                ]
            },
            {
                'title': 'Cinderella',
                'images': [
                    'images/upgraded balloon set-up/R8C.jpg',
                    'images/upgraded balloon set-up/R8A.jpg',
                    'images/upgraded balloon set-up/R8D.jpg',
                    'images/upgraded balloon set-up/R8B.jpg',
                ]
            },
            {
                'title': 'Blue Royalty',
                'images': [
                    'images/upgraded balloon set-up/R9C.jpg',
                    'images/upgraded balloon set-up/R9A.jpg',
                    'images/upgraded balloon set-up/R9D.jpg',
                    'images/upgraded balloon set-up/R9B.jpg',
                ]
            },
            {
                'title': 'Pink Floral',
                'images': [
                    'images/upgraded balloon set-up/R10C.jpg',
                    'images/upgraded balloon set-up/R10A.jpg',
                    'images/upgraded balloon set-up/R10D.jpg',
                    'images/upgraded balloon set-up/R10B.jpg',
                ]
            },
            {
                'title': 'Mermaid and Sea Life',
                'images': [
                    'images/upgraded balloon set-up/R11C.jpg',
                    'images/upgraded balloon set-up/R11A.jpg',
                    'images/upgraded balloon set-up/R11D.jpg',
                    'images/upgraded balloon set-up/R11B.jpg',
                ]
            },
            {
                'title': 'Barbie',
                'images': [
                    'images/upgraded balloon set-up/R12C.jpg',
                    'images/upgraded balloon set-up/R12A.jpg',
                    'images/upgraded balloon set-up/R12D.jpg',
                    'images/upgraded balloon set-up/R12B.jpg',
                ]
            },
            {
                'title': 'Butterfly Garden',
                'images': [
                    'images/upgraded balloon set-up/R13C.jpg',
                    'images/upgraded balloon set-up/R13A.jpg',
                    'images/upgraded balloon set-up/R13D.jpg',
                    'images/upgraded balloon set-up/R13B.jpg',
                ]
            },
        ],
        'minimalist_setup': [
            {
                'title': 'Red & White Roses',
                'images': [
                    'images/minimalist set-up/R1C.jpg',
                    'images/minimalist set-up/R1A.jpg',
                    'images/minimalist set-up/R1D.jpg',
                    'images/minimalist set-up/R1B.jpg',
                ]
            },
            {
                'title': 'Ivory Simplicity',
                'images': [
                    'images/minimalist set-up/R2C.jpg',
                    'images/minimalist set-up/R2A.jpg',
                    'images/minimalist set-up/R2D.jpg',
                    'images/minimalist set-up/R2B.jpg',
                ]
            },
            {
 'title': 'Mint Serenity',
                'images': [
                    'images/minimalist set-up/R3C.jpg',
                    'images/minimalist set-up/R3A.jpg',
                    'images/minimalist set-up/R3D.jpg',
                    'images/minimalist set-up/R3B.jpg',
                ]
            },
            {
                'title': 'Amethyst Grace',
                'images': [
                    'images/minimalist set-up/R4C.jpg',
                    'images/minimalist set-up/R4A.jpg',
                    'images/minimalist set-up/R4D.jpg',
                    'images/minimalist set-up/R4B.jpg',
                ]
            },
            {
                'title': 'Sage Whispers',
                'images': [
                    'images/minimalist set-up/R5C.jpg',
                    'images/minimalist set-up/R5A.jpg',
                    'images/minimalist set-up/R5D.jpg',
                    'images/minimalist set-up/R5B.jpg',
                ]
            },
            {
                'title': 'Golden Crimson',
                'images': [
                    'images/minimalist set-up/R6C.jpg',
                    'images/minimalist set-up/R6A.jpg',
                    'images/minimalist set-up/R6D.jpg',
                    'images/minimalist set-up/R6B.jpg',
                ]
            },
            {
                'title': 'Maroon Muse',
                'images': [
                    'images/minimalist set-up/R7C.jpg',
                    'images/minimalist set-up/R7A.jpg',
                    'images/minimalist set-up/R7D.jpg',
                    'images/minimalist set-up/R7B.jpg',
                ]
            },
            {
                'title': 'Ever After Eden',
                'images': [
                    'images/minimalist set-up/R8C.jpg',
                    'images/minimalist set-up/R8A.jpg',
                    'images/minimalist set-up/R8D.jpg',
                    'images/minimalist set-up/R8B.jpg',
                ]
            },
            {
                'title': 'Whispering Vows',
                'images': [
                    'images/minimalist set-up/R9C.jpg',
                    'images/minimalist set-up/R9A.jpg',
                    'images/minimalist set-up/R9D.jpg',
                    'images/minimalist set-up/R9B.jpg',
                ]
            },
        ],
        'signature_setup': [
            {
                'title': 'Sunlit Bliss',
                'images': [
                    'images/signature set-up/R1C.jpg',
                    'images/signature set-up/R1A.jpg',
                    'images/signature set-up/R1E.jpg',
                    'images/signature set-up/R1F.jpg',
                    'images/signature set-up/R1B.jpg',
                    'images/signature set-up/R1D.jpg',
                ]
            },
            {
                'title': 'Forest Glow',
                'images': [
                    'images/signature set-up/R2C.jpg',
                    'images/signature set-up/R2A.jpg',
                    'images/signature set-up/R2E.jpg',
                    'images/signature set-up/R2F.jpg',
                    'images/signature set-up/R2B.jpg',
                    'images/signature set-up/R2D.jpg',
                ]
            },
            {
                'title': 'Blue Royale',
                'images': [
                    'images/signature set-up/R3C.jpg',
                    'images/signature set-up/R3A.jpg',
                    'images/signature set-up/R3E.jpg',
                    'images/signature set-up/R3F.jpg',
                    'images/signature set-up/R3B.jpg',
                    'images/signature set-up/R3D.jpg',
                ]
            },
            {
                'title': 'Golden Dusk',
                'images': [
                    'images/signature set-up/R4C.jpg',
                    'images/signature set-up/R4A.jpg',
                    'images/signature set-up/R4E.jpg',
                    'images/signature set-up/R4F.jpg',
                    'images/signature set-up/R4B.jpg',
                    'images/signature set-up/R4D.jpg',
                ]
            },
        ],
    }    
    return render(request, 'moredesign.html', {'sets': sets})