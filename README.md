# Accessible Forums
## Development guide
>**Note:** Run all the commands in the project root directory
- Create a python 3 environment using your favorite environment manager. For example, conda users:
```bash
conda create -n accessible-forums python=3
```
- Activate the environment
```bash
conda activate accessible-forums
```
- Install all the dependencies using the requirements.txt file
```bash
pip install -r requirements.txt
```
- Initialize the database (uses the flask-migrate dependency)
```bash
flask db upgrade
```
- Before loading data into the database, copy the data files into the project root directory. The compressed data 
directory can be downloaded [here](https://drive.google.com/uc?export=download&id=1grOjuzYedwTrJ3-GTQqkMpegPCc3aT4a).
```bash
cp -r /path/to/data/directory ./
```
- After copying, the project root directory should look like this:  
```
📦accessible-forums  
 ┣ 📂app  
 ┣ 📂data  
 ┃ ┣ 📜...csv files  
 ┃ ┗ 📂folder (optional)  
 ┃   ┗ 📜...csv files  
 ┣ 📂migrations  
 ┣ 📜.env  
 ┣ 📜.gitignore  
 ┣ 📜babel.cfg  
 ┣ 📜config.py  
 ┣ 📜main.py  
 ┗ 📜requirements.txt
```
>**Note:** If you're going to use elasticsearch, now is a good time to start the elasticsearch server.
This will index the data into elasticsearch as we load them into db. 
You can set the ip and port of the elasticsearch server in the `.env` file.
- Use the following command to load the data into database:
```bash
flask db-load
```
- Run the app using
```bash
flask run -h 0.0.0.0
```
By default, the app will be running on http://127.0.0.1:5000/.
On a local network (WiFi), you can access the website through any device on the same network (WiFi) using the local 
ip address of the machine. E.g. If your machine has the local ip address 192.168.0.2, you can access the website using 
http://192.168.0.2:5000/. Use the `ifconfig` command on UNIX machines and `ipconfig` command on Windows machines to get 
the local ip address of the device.

## Credits
This project is heavily adopted from the excellent [Flask Mega-Tutorial by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).
