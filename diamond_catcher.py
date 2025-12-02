from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global variables
W_Width,W_Height=500,700
game_score=0
game_state=False
paused=False
cheat_mode = False

# Diamond properties
diamond_x_co=random.randint(60,W_Width-60)
diamond_y_co=W_Height-90
diamond_speed=1.3
diamond_acce=0.5
diamond_clr=random.choice([
    [1.0,0.0,0.0],    #  Red
    [0.0,1.0,0.0],    #  Green
    [0.0,0.0,1.0],    #  Blue
    [1.0,1.0,0.0],    #  Yellow
    [1.0,0.0,1.0],    #  Magenta
    [0.0,1.0,1.0],    #  Cyan
    [1.0,0.5,0.0],    #  Orange
    [0.5,0.0,1.0],    #  Purple
])

# Catcher properties
catcher_x_co=W_Width//2    #horizontal center
catcher_y_co=30
catcher_speed=300
catcher_width=100
catcher_height=20
catcher_clr=[1.0,1.0,1.0]

# Button properties
button_size=32
button_y=W_Height-52    #top of the screen

# Time tracking
last_time = time.time()

# Zone conversion functions (Midpoint line)

def zone_find(x_1,y_1,x2,y_2):
    d_x=x2-x_1
    d_y=y_2-y_1
    if abs(d_x)>=abs(d_y):
        if d_x>0 and d_y>0:
            return 0
        elif d_x<0 and d_y>0:
            return 3
        elif d_x<0 and d_y<0:
            return 4
        else:
            return 7
    else:
        if d_x>0 and d_y>0:
            return 1
        elif d_x<0 and d_y>0:
            return 2
        elif d_x<0 and d_y<0:
            return 5
        else:
            return 6

def convert_to_zone_0(x,y,zone):
    if zone==0: return x,y
    elif zone==1: return y,x
    elif zone==2: return y,-x
    elif zone==3: return -x,y
    elif zone==4: return -x,-y
    elif zone==5: return -y,-x
    elif zone==6: return -y,x
    elif zone==7: return x,-y

def convert_from_zone_0(x,y,zone):
    if zone==0: return x,y
    elif zone==1: return y,x
    elif zone==2: return -y,x
    elif zone==3: return -x,y
    elif zone==4: return -x,-y
    elif zone==5: return -y,-x
    elif zone==6: return y,-x
    elif zone==7: return x,-y

def mpl(x_1,y_1,x2,y_2):
    zone=zone_find(x_1,y_1,x2,y_2)
    x_1_0,y_1_0=convert_to_zone_0(x_1,y_1,zone)   #1st point
    x2_0,y_2_0=convert_to_zone_0(x2,y_2,zone)     #2nd point
    d_x=x2_0 - x_1_0
    d_y=y_2_0 - y_1_0
    d=2* d_y-d_x
    delE=2* d_y
    delNE=2*(d_y - d_x)
    y = y_1_0
    points=[]
    for x in range(x_1_0,x2_0 + 1):
        orig_x,orig_y=convert_from_zone_0(x,y,zone)
        points.append((orig_x,orig_y))
        if d>0:
            d+=delNE
            y+=1
        else:
            d+=delE
    return points

# Drawing primitives
def draw_points(points,color):
    glColor3f(*color)
    glPointSize(3)
    glBegin(GL_POINTS)
    for i in points:
        glVertex2f(i[0],i[1])  #a single point
    glEnd()

def draw_line(x_1,y_1,x2,y_2,color):
    points=mpl(int(x_1),int(y_1),int(x2),int(y_2))
    draw_points(points,color)

def draw_the_diamond(x,y,size,color):
    draw_line(x,y+size,x+size,y,color)   #top-right
    draw_line(x+size,y,x,y-size,color)   #right-bottom
    draw_line(x,y-size,x-size,y,color)   #bottom-left
    draw_line(x-size,y,x,y+size,color)   #left-top

def draw_the_catcher(x,y,width,height,color):
    half_width=width//2
    draw_line(x-half_width,y+height,x-half_width+10,y,color)  #left slanted line
    draw_line(x-half_width+10,y,x+half_width-10,y,color)   #bottom horizontal line
    draw_line(x+half_width-10,y,x+half_width,y+height,color)   #right slanted line
    draw_line(x-half_width,y+height,x+half_width,y+height,color)     #top line

# Buttons
def draw_restart_button(x,y,size):
    color=[0.0,0.8,0.8]
    draw_line(x+size//2,y-size//2,x-size//2,y,color)  #diagonal line down-left
    draw_line(x-size//2,y,x+size//2,y+size//2,color)   #diagonal line up-right
    draw_line(x-size//2,y,x+size//2,y,color)   #horizontal line in the middle
def draw_pause_button(x, y, size):
    color = [1.0, 0.85, 0.0]  # Bright Yellow
    half_size = size // 2
    bar_width = size // 5

    glColor3f(*color)

    if not paused:
        # Draw left bar using 2 triangles
        glBegin(GL_TRIANGLES)
        # Tri 1
        glVertex2f(x-bar_width-bar_width//2,y-half_size)
        glVertex2f(x-bar_width//2,y-half_size)
        glVertex2f(x-bar_width//2,y+half_size)
        # Tri 2
        glVertex2f(x-bar_width-bar_width//2,y-half_size)
        glVertex2f(x-bar_width//2,y+half_size)
        glVertex2f(x-bar_width-bar_width//2,y+half_size)

        # Draw right bar using 2 triangles
        # Tri 1
        glVertex2f(x+bar_width//2,y-half_size)
        glVertex2f(x+bar_width+bar_width//2,y-half_size)
        glVertex2f(x+bar_width+bar_width//2,y+half_size)
        # Tri 2
        glVertex2f(x+bar_width//2,y-half_size)
        glVertex2f(x+bar_width+bar_width//2,y+half_size)
        glVertex2f(x+bar_width//2,y+half_size)
        glEnd()
    else:
        # Draw play triangle (same as before)
        glBegin(GL_TRIANGLES)
        glVertex2f(x-size//3,y-half_size)
        glVertex2f(x-size//3,y+half_size)
        glVertex2f(x+size//3,y)
        glEnd()


def draw_close_button(x,y,size):
    color=[1.0,0.0,0.0]
    draw_line(x-size//2,y-size//2,x+size//2,y+size//2,color)    #bottom-left to top-right \
    draw_line(x-size//2,y+size//2,x+size//2,y-size//2,color)    #top-left to bottom-right /

# Collision check
def check_collision(x_1,y_1,w1,h1,x2,y_2,w2,h2):
    return (x_1-w1//2<x2+w2//2 and          #1-left,2-right
            x_1+w1//2>x2-w2//2 and           ##1-right,2-left
            y_1-h1//2<y_2+h2//2 and          #1-bottom,2-top
            y_1+h1//2>y_2-h2//2)

def reset_game():
    global game_score,game_state,diamond_x_co,diamond_y_co,diamond_speed,diamond_clr,catcher_clr,paused
    game_score=0
    game_state=False
    paused=False
    diamond_x_co=random.randint(50,W_Width-50)
    diamond_y_co=W_Height-50
    diamond_speed=2.0
    diamond_clr=random.choice([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0],[1.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0],
        [1.0, 0.5, 0.0], [0.5, 0.0, 1.0]
    ])
    catcher_clr = [1.0, 1.0, 1.0]
    print("Starting Over")

def spawn_new_diamond():
    global diamond_x_co, diamond_y_co,diamond_clr,diamond_speed
    diamond_x_co=random.randint(50,W_Width-50)
    diamond_y_co=W_Height-50
    diamond_clr=[random.random(),random.random(),random.random()]
    diamond_speed=diamond_speed+diamond_acce

def iterate():
    glViewport(0,0,W_Width,W_Height)   #draw inside the full game
    glMatrixMode(GL_PROJECTION)      #controls the camera view.
    glLoadIdentity()
    glOrtho(0.0, W_Width, 0.0, W_Height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global diamond_y_co,game_score,game_state,catcher_clr,last_time,catcher_x_co  #update
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glClearColor(0.0, 0.0, 0.0, 0.0)

    # delta time
    curr_time=time.time()
    dt=curr_time - last_time
    last_time=curr_time

    # update diamond
    if not game_state and not paused:
        diamond_y_co -= diamond_speed

        # cheat mode movement
        if cheat_mode:
            if catcher_x_co<diamond_x_co:    #left,,move right
                catcher_x_co+=min(catcher_speed*dt,diamond_x_co-catcher_x_co)   #moves right smoothly
            elif catcher_x_co>diamond_x_co:
                catcher_x_co-=min(catcher_speed*dt,catcher_x_co-diamond_x_co)

        # collision detection
        if check_collision(catcher_x_co,catcher_y_co,catcher_width,catcher_height,
                           diamond_x_co, diamond_y_co,20,20):
            game_score+=1
            print(f"game_score:{game_score}")
            spawn_new_diamond()     #create new

        # miss check
        if diamond_y_co<0:   #below screen
            game_state=True
            catcher_clr=[1.0,0.0,0.0]   #red
            print(f"Game Over! Final game_score:{game_score}")

    # draw objects
    if not game_state:
        draw_the_diamond(diamond_x_co,diamond_y_co,10, diamond_clr)

    draw_the_catcher(catcher_x_co,catcher_y_co,catcher_width,catcher_height,catcher_clr)

    # UI buttons
    draw_restart_button(50,button_y,button_size)
    draw_pause_button(W_Width//2,button_y,button_size)

    draw_close_button(W_Width-50,button_y,button_size)

    glutSwapBuffers()

def animate(value):
    glutPostRedisplay()
    glutTimerFunc(15,animate,0)

def keyboardListener(key,x,y):
    global catcher_x_co
    if not game_state and not paused:
        if key==GLUT_KEY_LEFT:
            catcher_x_co=max(catcher_width//2,catcher_x_co-20)
        elif key==GLUT_KEY_RIGHT:
            catcher_x_co=min(W_Width-catcher_width//2,catcher_x_co+20)
    glutPostRedisplay()

def normalKeyListener(key,x,y):
    global cheat_mode
    if key in (b'c', b'C'):
        cheat_mode=not cheat_mode
        print(f"Cheat Mode: {'ON' if cheat_mode else 'OFF'}")
    glutPostRedisplay()

def mouseListener(button,state,x,y):
    global paused
    if button==GLUT_LEFT_BUTTON and state==GLUT_DOWN:
        mouse_y_co=W_Height-y

        if abs(x-50)<button_size and abs(mouse_y_co-button_y)<button_size:
            reset_game()
        elif abs(x-W_Width//2)<button_size and abs(mouse_y_co-button_y)<button_size:
            paused=not paused
            print("Paused" if paused else "Resumed")
        elif abs(x-(W_Width-50))<button_size and abs(mouse_y_co-button_y)<button_size:
            print(f"Goodbye! Final game_score:{game_score}")
            glutLeaveMainLoop()

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_DEPTH)
    glutInitWindowSize(W_Width,W_Height)
    glutInitWindowPosition(100,100)
    glutCreateWindow(b"Catch the Diamonds!")
    glutDisplayFunc(showScreen)
    glutSpecialFunc(keyboardListener)
    glutKeyboardFunc(normalKeyListener)
    glutMouseFunc(mouseListener)
    glutTimerFunc(0,animate,0)
    glutMainLoop()

if __name__ == "__main__":
    main()