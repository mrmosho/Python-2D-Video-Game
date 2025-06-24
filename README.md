# Lost in the Dark

A 2D top-down adventure game built with Python and Pygame where players navigate through dark levels with a flashlight, collect coins, battle enemies, and face a final boss.

## 🎮 Game Overview

Lost in the Dark is a survival adventure game featuring:
- **3 Unique Levels**: Progress through increasingly challenging environments
- **Flashlight Mechanics**: Navigate in darkness with a directional flashlight
- **Enemy Combat**: Face various enemies and a challenging boss fight
- **Projectile System**: Use ranged attacks against the final boss
- **Coin Collection**: Gather coins throughout your journey
- **Progressive Difficulty**: Each level introduces new challenges

## 🕹️ Controls

- **Arrow Keys**: Move your character (Up, Down, Left, Right)
- **Space Bar**: Fire projectiles (Boss level only)
- **Enter**: Confirm menu selections
- **Escape**: Pause/Resume game
- **Arrow Keys**: Navigate menus

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd lost-in-the-dark
   ```

2. **Install dependencies**
   ```bash
   pip install pygame
   ```
   
   Or if you have a requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create the assets folder structure**
   ```bash
   mkdir assets
   ```

4. **Add your game assets** (optional - the game will use defaults if assets are missing)
   - Place your images and sounds in the `assets/` folder following the structure above

5. **Run the game**
   ```bash
   python game.py
   ```

## 🎨 Asset Requirements

### Images
- **Format**: PNG recommended
- **Player**: 20x20 pixels
- **Enemy**: 30x30 pixels  
- **Coin**: 10x10 pixels
- **Backgrounds**: Will be automatically scaled to 800x600

### Audio
- **Format**: WAV files only
- **Recommended**: 16-bit, 44.1kHz sample rate
- **File naming**: Must match exactly as listed in project structure

### Optional Assets
The game includes fallback graphics and silent audio if asset files are missing, so you can run the game immediately without any custom assets.

## 🎯 Game Features

### Level 1 & 2: Exploration
- Navigate through dark environments
- Collect coins scattered throughout the level
- Avoid or confront enemies
- Find the door to progress to the next level
- Use your flashlight to see in the darkness

### Level 3: Boss Fight
- Face the final boss in an arena-style battle
- Use projectile attacks (Space bar) to damage the boss
- Dodge boss attacks including:
  - **Laser attacks**: Targeted beam attacks
  - **Stomp attacks**: Area-of-effect damage
  - **Punch attacks**: Close-range strikes
- Defeat the boss to win the game

### Special Mechanics
- **Flashlight**: Illuminates a cone in your facing direction
- **Collision System**: Realistic wall and obstacle collision
- **Health System**: Track your health throughout the game
- **Progressive Difficulty**: Each level increases in challenge

## ⚙️ Game Settings

Access the settings menu from the main menu to toggle:
- **Custom Models**: Enable/disable custom sprite graphics
- **Custom Sounds**: Enable/disable sound effects and music

## 🐛 Troubleshooting

### Common Issues

**Game won't start:**
- Ensure Python 3.7+ is installed
- Install pygame: `pip install pygame`
- Check that `game.py` is in the current directory

**Missing graphics/sounds:**
- The game will run with default graphics if assets are missing
- Create an `assets/` folder and add your files
- Ensure file names match exactly (case-sensitive)

**Poor performance:**
- Close other applications
- Ensure your system meets minimum requirements
- Try reducing window size in the code if needed

**Audio not working:**
- Check system audio settings
- Ensure audio files are in WAV format
- Verify pygame audio is properly initialized

## 🔧 Customization

### Modifying Game Constants
Edit the constants at the top of `game.py`:
```python
WIDTH, HEIGHT = 800, 600  # Window size
PLAYER_SPEED = 5          # Player movement speed
ENEMY_SPEED = 2           # Enemy movement speed
FLASHLIGHT_LENGTH = 200   # Flashlight range
```

### Adding New Levels
1. Create new level maps in the `generate_level()` function
2. Add corresponding background images
3. Update level progression logic

### Custom Assets
- Replace any file in the `assets/` folder with your own
- Maintain the same file names and formats
- Images will be automatically scaled as needed

## 🎵 Credits

### Engine
- Built with [Pygame](https://www.pygame.org/) - Cross-platform set of Python modules designed for writing video games

### Development
- Game design and programming: [Your Name]
- Sound effects: [Attribution if using external sounds]
- Graphics: [Attribution if using external graphics]

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the game code comments
3. Open an issue in the repository
4. Contact the development team

---

**Enjoy your adventure in the dark! 🔦**
