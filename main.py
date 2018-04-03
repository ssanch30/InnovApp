import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button 
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
import pymysql as db
from kivy.lang import Builder
from os.path import dirname, join
from collections import namedtuple
import numpy as np
from functools import partial
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock

kivy.config.Config.set ( 'input', 'mouse', 'mouse,disable_multitouch' )


class Inno2Screen(Screen):
    fullscreen = BooleanProperty(False)
    acc= ObjectProperty()

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(Inno2Screen, self).add_widget(*args)



connection = db.connect(host='localhost',
									port = 3306, 
		                            user='root',
		                            password='root',
		                            db='innovapp',
		                            charset='utf8mb4',
		                            cursorclass=db.cursors.DictCursor)
cursor=connection.cursor()


class InnovApp(App):

    index = NumericProperty(-1)
    current_title = StringProperty()
    time = NumericProperty(0)
    show_sourcecode = BooleanProperty(False)
    sourcecode = StringProperty()
    screen_names = ListProperty([])
    hierarchy = ListProperty([])
    user_info = ObjectProperty()
    userinput =  ObjectProperty()
    idea_id = NumericProperty()
    ideaInfo = ObjectProperty()
    curdir = dirname(__file__)
    innovador = StringProperty()
    typpe = StringProperty()
    state = StringProperty()
    idea = StringProperty()
    description = StringProperty()
    situacion = StringProperty()
    flag = StringProperty()
    puntos = StringProperty()
    responsable = StringProperty()

    ######### CAMBIAR ESTO a TRUE EN CASO DE PRUEBAS##########
    ##########################################################
    debug = False
    

    ##########################################################
    ##########################################################
    def build(self):
        self.title = 'INNOVAPP'
        self.screens = {}
        self.available_screens = ['login', 'menu2', 'embudo', 'postulacion', 'estado', 'incentivos', 'registro', 'social', 'ideas']
        self.screen_names = self.available_screens
        self.available_screens = [join(self.curdir, 'data', 'screens',
            '{}.kv'.format(fn).lower()) for fn in self.available_screens]
        self.go_next_screen()
        # return self, CustomTP()
    


    def go_next_screen(self):
        if self.debug == True:
            self.index = (self.index + 2) % len(self.available_screens)
        else:
            self.index = (self.index + 1) % len(self.available_screens)

        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='left')
        self.current_title = screen.name

    def go_screen(self, idx):
        self.index = idx
        self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')


    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index])
        self.screens[index] = screen
        return screen

    def valid_user(self, user_info):
        try:
            sql = " SELECT `password` FROM `usuario` WHERE `email`= %s"
            cursor.execute(sql, (user_info.uLogin))
            result = cursor.fetchone()
        finally:
            if result == None:
                    print("Nomre de usuario incorrecto, verificalo e intenta nuevamente")
            else:
                result = list(result.values())
                #print(result[0])
                if result[0] == user_info.pLogin: 
                    print ("Inicio de sesion correcto")
                    self.go_screen(1)
                else :
                    print("nombre de usuario o contraeña incorrecto")
       


    def sign_up(self, userinput):
        try:
            # Create a new record
            sql = "INSERT INTO `usuario` (`nombre`,`apellido`,`email`,`password`,`cargo`) VALUES (%s, %s,%s,%s,%s)"
            cursor.execute(sql, (userinput.nombre, userinput.apellido,userinput.email, userinput.passwd, userinput.cargo))
            connection.commit()
            sql = "SELECT `usr_id`, `password` FROM `usuario` WHERE `email`=%s"
            cursor.execute(sql, ('b'))
            result = cursor.fetchone()
            print(result)
        finally:
            connection.close()


    def go_screen_tab(self, idx, layout):
        self.index = idx
        layout.clear_widgets()
        screen = layout.add_widget(Builder.load_file(self.available_screens[self.index]))
        if self.index in self.screens:
            return self.screens[self.index]
        if not layout.get_parent_window():
            return
        self.screens[self.index] = screen
        return screen

    def extract_idea2(self, nombre, apellido, type_name, state_name, idea_name, idea_description, puntos, situacion_actual, flag_name,responsable):
        self.innovador = (nombre + " " + apellido)
        self.typpe = type_name
        self.state = state_name
        self.responsable = responsable
        self.idea = idea_name
        self.description = idea_description
        self.puntos = str(puntos) 
        self.situacion = situacion_actual 
        self.flag = flag_name
        return self 

    def search_idea(self, idea_id):
        try:
            sql ="""SELECT usuario.nombre, usuario.apellido, type.type_name, state.state_name,idea.responsable,  idea.idea_name, idea.idea_description, idea.puntos, idea.situacion_actual,flag.flag_name
                    FROM idea
                        JOIN usuario
                            ON usuario.usr_id = idea.usr_id
                        JOIN type
                            ON type.type_id = idea.type_id
                        JOIN state
                            ON state.state_id = idea.state_id
                        JOIN flag
                            ON flag.flag_id = idea.flag_id
                    WHERE idea.idea_id = %s"""
            cursor.execute (sql,(idea_id))
            idea_results = cursor.fetchone()
            
            if idea_results == None:
                msg='La idea numero {} no se encuentra en la base de datos'.format(idea_id)
                ideaInfo = self.extract_idea2('','','','','',msg,'','','','')
            else:
                ideaInfo = self.extract_idea2(**idea_results)
            #print(ideaInfo.idea)
            #idea_info = self.extract_idea(idea_results)
            #print(idea_info.ideaDesc)
        finally:
            pass


class CustomTP(TabbedPanel):
    tp = ObjectProperty()
    do_default_tab = BooleanProperty(False)
    buttons= {}
    cur_tab= ObjectProperty()
    #header = ObjectProperty(None)
    # def __init__(self, **kwargs):    
    #     super(CustomTP, self).__init__()
    idNumber = NumericProperty()


    def switch_to(self, header):
        print(header.text)
        # set the Screen manager to load  the appropriate screen
        # linked to the tab head instead of loading content
        self.tp.current = header.screen
        # we have to replace the functionality of the original switch_to
        self.current_tab.state = "normal"
        header.state = 'down'
        self._current_tab = header
  
        return self._current_tab


    def generateLists(self,num):
        conceptList=[]
        ideaList=[]
        dlloPreList=[]
        protoList=[]
        validList=[]
        impList=[]

        rowlist=[]
        state_index=0
        idea_index=0
        idea_id_index=0 
        sql = """SELECT idea.idea_name, idea.idea_id, state.state_name, state.state_id, idea.type_id
                FROM idea
                    JOIN state
                        ON state.state_id = idea.state_id
                WHERE idea.state_id = %s"""

        for i in range(1,7):
            cursor.execute(sql,(i))

            ##rowlist=cursor.fetchmany(size = 20)
            #print(rowlist)
        
            while True:
                row = cursor.fetchone()
                #print (row)
                if row == None:
                    break 
                rowlist.append(row)
        for i in range(0,len(rowlist)):
            result = rowlist[i]
            result = np.array(list(result.items()))
            #print(result)

            j=0
            while True:
                state_index = j
                j=j+1
                if j > 10 or result[j-1][0]=='state_id':
                    break
            k=0
            while True:
                idea_index = k
                k=k+1
                if k > 10 or result[k-1][0]=='idea_name':
                    break
            h=0
            while True:
                idea_id_index = h
                h=h+1
                if h > 10 or result[h-1][0]=='idea_id':
                    break
            f=0
            while True:
                type_index = f
                f=f+1
                if f > 10 or result[f-1][0]=='type_id':
                    break
            #print(self.state_index, self.idea_index, self.idea_id_index)
            #print(result[self.state_index][1])

            if result[state_index][1] == '1':
                ideaList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])
            
            if result[state_index][1] == '2':
                conceptList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])

            if result[state_index][1] == '3':
                dlloPreList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])

            if result[state_index][1] == '4':
                protoList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])

            if result[state_index][1] == '5':
                validList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])
            
            if result[state_index][1] == '6':
                impList.append([result[idea_index][1], result[idea_id_index][1], result[type_index][1]])        
        if num == 1:
            return ideaList 
        if num == 2:
            return conceptList 
        if num == 3: 
            return dlloPreList
        if num == 4: 
            return protoList
        if num == 5: 
            return validList
        if num == 6:
            return impList 

    def createPopUp(self,idNum, idName,args):
        InnovApp.idea_id = idNum
        self.idNumber = idNum 
        popup = verMas(title=str(idNum)+'.'+ ' '+idName,
        size_hint=(None, None), size=(600, 600))
        verMas.idNum = self.idNumber

        return popup.open()

    def BuildButtonsss(self,blist,layout,buttons):
        #print(len(blist))
        i=0
        for i in range(0,len(blist)):
            layout.buttons[str(i)]=Button(text=blist[i][1]+'.'+' '+blist[i][0], size_hint_y=None, height=60)
            #print (layout.buttons[str(i)].text)
            if layout.buttons[str(i)] != None:
                layout.buttons[str(i)].bind(on_release = partial(self.createPopUp, int(blist[i][1]),blist[i][0]))
                layout.add_widget(layout.buttons[str(i)])


    def BuildButtonss(self,blist,layout,buttons):
        layout = BoxLayout(orientation = 'vertical' ,size_hint_y=None, size_hint_x = 1)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for i in range(3):
            btn = Button(text=str(i),  size_hint_y=None, height=60, width= 300)
            layout.add_widget(btn)
        return layout     
        # root = ScrollView(size_hint=(1, None),size=(layout.width, layout.height))
        # root.add_widget(layout)
        # i=0
        # for i in range(0,len(blist)):
        #     layout.buttons[str(i)]=Button(text=blist[i][1]+'.'+' '+blist[i][0], size_hint_y=None, height=60)
        #     #print (layout.buttons[str(i)].text)
        #     if layout.buttons[str(i)] != None:
        #         layout.buttons[str(i)].bind(on_release = partial(self.createPopUp, int(blist[i][1]),blist[i][0]))
        #         layout.add_widget(layout.buttons[str(i)])
        # return layout


    def BuildButtons(self,blist,layout):
        i=0
        for i in range(0,len(blist)):
            btn=Button(text=blist[i][1]+'.'+' '+blist[i][0], size_hint_y=None, height=60)
            #print (layout.buttons[str(i)].text)
            if btn != None:
                btn.bind(on_release = partial(self.createPopUp, int(blist[i][1]),blist[i][0]))
                layout.add_widget(btn)


class verMas(Popup):
    idNum = NumericProperty()


class CustGrid(GridLayout):
    rootClss = CustomTP()
    blist = rootClss.generateLists(1)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs): 
        super(CustGrid, self).__init__(**kwargs)
        self.rootClss.BuildButtons(self.blist,self)

        

class CustGridTest(GridLayout):
    rootClss = CustomTP()
    blist = rootClss.generateLists(4)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs): 
        super(CustGridTest, self).__init__(**kwargs)
        #self.rootClss.createAccContent(1,self)
        self.rootClss.BuildButtons(self.blist,self)





class CustGrid2(GridLayout):
    rootClass = CustomTP()
    blist = rootClass.generateLists(2)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs):
        super(CustGrid2, self).__init__(**kwargs)
        self.rootClass.BuildButtons(self.blist,self)

class CustGrid3(GridLayout):
    rootClass = CustomTP()
    blist = rootClass.generateLists(3)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs):
        super(CustGrid3, self).__init__(**kwargs)
        self.rootClass.BuildButtons(self.blist,self)





class CustGrid4(GridLayout):
    buttons = {}
    rootClass = CustomTP()
    blist = rootClass.generateLists(4)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs):
        super(CustGrid4, self).__init__(**kwargs)
        self.rootClass.BuildButtons(self.blist,self)



class CustGrid5(GridLayout):
    rootClass = CustomTP()
    blist = rootClass.generateLists(5)
    rows = int(1+ (len(blist)/3))
    def __init__(self, **kwargs):
        super(CustGrid5, self).__init__(**kwargs)
        self.rootClass.BuildButtons(self.blist,self)

class CustGrid6(GridLayout):
    rootClass = CustomTP()
    blist = rootClass.generateLists(6)
    rows = int(1+ (len(blist)/3))

    def __init__(self, **kwargs):
        super(CustGrid6, self).__init__(**kwargs)
        self.rootClass.BuildButtons(self.blist,self)



    












if __name__ == '__main__':
	InnovApp().run()



