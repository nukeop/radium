import pygame


class DebugInfo:
    def __init__(self):
        self.surface = pygame.Surface((100, 100))
        self.font = pygame.font.SysFont(None, 20)

    def draw(self, memory):
        self.surface.fill(pygame.Color('black'))

        debug_text = self.font.render("Debug mode", True,
                                      pygame.Color('white'))

        debug_mem_text = self.font.render("Memory:", True,
                                          pygame.Color('white'))

        self.surface.blit(debug_text, (0, 0))
        self.surface.blit(debug_mem_text, (0, 20))

        mem_surface = pygame.Surface((64, 64))

        for i in range(64):
            for j in range(64):
                mem = memory[i + j*64]
                mem_surface.set_at(
                    (i, j),
                    pygame.Color(mem, 0, 0)
                )

        self.surface.blit(pygame.transform.scale(mem_surface, (128, 128)), (0, 40))


        return self.surface


class Interface:
    def __init__(self, width=64, height=32, scale=1, debug=False):
        pygame.init()

        self.width = width
        self.height = height
        self.scale = scale

        window_width = self.width*self.scale
        window_height = self.height*self.scale

        self.debug = debug
        if self.debug:
            window_width += 128
            self.debug_info = DebugInfo()

        self.screen = pygame.display.set_mode(
            (window_width, window_height)
        )
        self.surface = pygame.Surface((self.width, self.height))

        self.colors = [pygame.Color('black'),
                       pygame.Color('white')]


    def clear(self):
        self.surface.fill(self.colors[0])


    def draw(self, display, memory=None):
        self.clear()
        self.surface = pygame.Surface((self.width, self.height))

        for i in range(32*64):
            if display[i] == 1:
                self.surface.fill(self.colors[1], ((i%64, 31-i//64), (1, 1)))

        pygame.display.get_surface().blit(
            pygame.transform.scale(
                pygame.transform.flip(self.surface, False, True),
                (self.width*self.scale, self.height*self.scale)
            ),
            (0, 0)
        )

        if self.debug:
            debug_surf = self.debug_info.draw(memory)
            pygame.display.get_surface().blit(debug_surf,
                                              (self.width*self.scale, 0))

        pygame.display.update()


    def handle_events(self):
        events = pygame.event.get()

        quit_events = [e for e in events if e.type == pygame.QUIT]
        if len(quit_events) > 0:
            pygame.quit()
            exit()

        return events
