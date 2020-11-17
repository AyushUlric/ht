from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform 
from kivymd.toast import toast
from kivymd.uix.list import ThreeLineListItem,OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.core.clipboard import Clipboard
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.screenmanager import Screen,ScreenManager,SlideTransition
import pyrebase

mobile = None
firebase_config = {
	"apiKey": "AIzaSyCpB9fglh7Lh6gZlX-9MSvTgEww6y61Z4w",
	"authDomain": "hospitele-app.firebaseapp.com",
	"databaseURL": "https://hospitele-app.firebaseio.com",
	"storageBucket": "hospitele-app.appspot.com"
}
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
storage = firebase.storage()

class AuthScreen(Screen):
	pass

class OngoingOrders(Screen):
	def reload(self):
		self.ids.container.clear_widgets()
		x = db.child('PendingOrders').get()
		print(x.val())
		if x.val() is None:
			self.ids.container.add_widget(OneLineListItem(text='No New Pending Deliveries Found.'))
		else:
			for a in x.each():
				data = a.val()
				y = db.child('Users').child(data['mobile']).get().val()
				mobile = data['mobile']
				ans = f"{y['Address']}-{y['ZipCode']}, {y['Name']}"
				self.ids.container.add_widget(ThreeLineListItem(text=ans,secondary_text=f"{y['Mobile']}",
					tertiary_text=f"{data['Products']}, ₹{data['Billed Ammount']}",
					on_release = lambda x,ndata=data,ny=y,mobileNumber=mobile:self.showDetails(f"""---Product Details---\n
{ndata['Products']} {ndata['Description']}
Quantity {ndata['quantity']}\nSales Price {ndata['mrp']} each\n
Pending Ammount ₹{ndata['Billed Ammount']}\n\n
Ordered On {ndata['date and time']}\n\n
---Customer Details---\n
{ny['Name']}\n
{ny['Mobile']}\n
{ny['Address']}-{ny['ZipCode']}""",mobileNumber)))
				
	def showDetails(self,*args):
		global mobile
		mobile = args[1]
		details = str(args[0])
		close_button = MDFillRoundFlatButton(text='Close',on_release=self.close_dialog)
		delivered_button = MDFillRoundFlatButton(text='Delivered',on_release=self.delivered)
		copy_button = MDFillRoundFlatButton(text='Copy Mobile Number',on_release=self.copy_number)
		self.dialog = MDDialog(title='Product Details',text= details,size_hint=(0.95,1),
			buttons=[close_button,copy_button,delivered_button])
		self.dialog.open()

	def close_dialog(self,obj):
		self.dialog.dismiss()
	
	def close_Ndialog(self,obj):
		self.Ndialog.dismiss()
	
	def delivered(self,obj):
		close_button = MDFillRoundFlatButton(text='Cancel',on_release=self.close_Ndialog)
		confirm_button = MDFillRoundFlatButton(text='Confirm',on_release=self.conf_delivered)
		self.Ndialog = MDDialog(title='Confirm',text= 'Remove This Order From Pending Deliveries?',size_hint=(0.95,1),
			buttons=[close_button,confirm_button])
		self.Ndialog.open()
	
	def conf_delivered(self,obj):
		db.child('PendingOrders').child(mobile).remove()
		toast('Delivery Complete!')
		self.reload()
		self.Ndialog.dismiss()
		self.dialog.dismiss()

	def copy_number(self,obj):
		Clipboard.copy(str(mobile))
		toast('Mobile Number Copied To Clipboard')

class ScreenManager(ScreenManager):
	pass

class MainApp(MDApp):
	
	def build(self):
		self.theme_cls.primary_palette = 'DeepOrange'
		master = Builder.load_file('main.kv')
		return master
	
MainApp().run()