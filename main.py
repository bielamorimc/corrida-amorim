"""Corridas Amorim — entry point."""
import sys

import pygame

from audio import SoundManager
from settings import FPS, HEIGHT, TITLE, WIDTH
from states import MenuState


def main() -> None:
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    audio = SoundManager()
    state = MenuState(audio)

    while state is not None:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                state = None
                break
        if state is None:
            break

        next_state = state.handle_events(events)
        if next_state is None:
            break
        state = next_state

        next_state = state.update(dt)
        if next_state is None:
            break
        state = next_state

        state.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
