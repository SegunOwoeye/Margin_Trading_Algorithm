import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 400, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Shape Shifter")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Shape
shape = pygame.Rect(width // 2 - 20, 50, 40, 40)  # Start as a square
shape_color = white
rotation_angle = 0
rotation_speed = 2

# Wall
wall_gaps = []  # List to store gap positions
wall_speed = 3

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                shape.x -= 10  # Move left
            if event.key == pygame.K_RIGHT:
                shape.x += 10  # Move right
            if event.key == pygame.K_SPACE:
                rotation_angle += 45  # Rotate shape

    # Rotate the shape
    shape = pygame.transform.rotate(shape, rotation_angle)

    # Move the wall down
    for gap in wall_gaps:
        gap[1] += wall_speed

    # Generate new gaps in the wall
    if wall_gaps[-1][1] > 100:  # Add a new gap when the last one is far enough down
        wall_gaps.append([random.randint(0, width - 50), 0, 50])  # Gap width is 50

    # Remove gaps that are off the screen
    wall_gaps = [gap for gap in wall_gaps if gap[1] < height]

    # Check for collision with wall
    for gap in wall_gaps:
        if shape.colliderect(pygame.Rect(gap[0], gap[1], width - gap[2], 20)):
            running = False  # Game over

    # Fill the screen
    screen.fill(black)

    # Draw the wall
    for gap in wall_gaps:
        pygame.draw.rect(screen, white, (0, gap[1], gap[0], 20))
        pygame.draw.rect(screen, white, (gap[0] + gap[2], gap[1], width - gap[0] - gap[2], 20))

    # Draw the shape
    pygame.draw.rect(screen, shape_color, shape)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(30)

# Quit Pygame
pygame.quit()