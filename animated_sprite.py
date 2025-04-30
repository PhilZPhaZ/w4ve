import pygame
from settings import WIDTH, HEIGHT

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, images):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation.
        """
        super(AnimatedSprite, self).__init__()

        size = (32, 32)  # This should match the size of the images.

        self.rect = pygame.Rect(position, size)
        self.images = images
        self.images_right = images
        self.images_left = [pygame.transform.flip(image, True, False) for image in images]  # Flipping every image.
        self.index = 0
        self.image = images[self.index]  # 'image' is the current image of the animation.

        self.velocity = pygame.math.Vector2(3, 0)

        self.animation_time = 0.01
        self.current_time = 0

        self.animation_frames = 6
        self.current_frame = 0
        
        self.dead = False
        self.gravity = 0.5
        self.rotation = 0
        self.rotation_speed = 5
        self.velocity_y = 0

    def update_time_dependent(self, dt):
        """
        Updates the image of Sprite approximately every 0.1 second.

        Args:
            dt: Time elapsed between each frame.
        """
        if self.velocity.x > 0:  # Use the right images if sprite is moving right.
            self.images = self.images_right
        elif self.velocity.x < 0:
            self.images = self.images_left

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.rect.move_ip(*self.velocity)
        if self.rect.left > WIDTH:
            self.rect.right = 0

    def update(self, dt):
        """This is the method that's being called when 'all_sprites.update(dt)' is called."""
        if self.dead:
            self.update_death(dt)
        else:
            self.update_time_dependent(dt)

    
    def draw(self, screen):
        """
        Draws the sprite on the screen.

        Args:
            screen: The screen to draw the sprite on.
        """
        screen.blit(self.image, self.rect)
    
    def update_death(self, dt):
        # Petit saut initial puis gravité
        self.velocity_y += self.gravity
        self.rect.y += int(self.velocity_y)
        self.rotation += self.rotation_speed

        # Appliquer la rotation à l'image
        rotated_image = pygame.transform.rotate(self.images[self.index], self.rotation)
        self.image = rotated_image
        # Centrer le rect sur la nouvelle image
        self.rect = self.image.get_rect(center=self.rect.center)

    def death(self):
        """
        Kill the spritte with gravity effect and spinning effect
        """
        self.dead = True
        self.velocity.x = 0
        self.velocity_y = -10
        self.rotation_speed = 10
