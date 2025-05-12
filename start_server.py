from clean_app import app

if __name__ == '__main__':
    print("Starting USB Monitoring System...")
    print("Open your browser and navigate to: http://localhost:5000/real_dashboard.html")
    app.run(debug=True)
