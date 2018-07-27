"""
This Project is Licenced under GPL 3.0 

	authors credit:
		abdullah.alsaidi16@gmail.com (Abdullah Alsaidi)
		husen.issa95@gmail.com		 (Husen Issa)
		




"""
import cv2
import numpy as np

# variable for distance with the coming vehicle
x = 0
# variable for detect (crop image) the coming vehicles one time only
a=0
font = cv2.FONT_HERSHEY_TRIPLEX

# This function to initiate a region of interst for the meanshift algorithm
def roi_meanshift(frame , n_chnl,y,h,x,w):
	global roi_hist , term_crit , hsv
	hsv = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)
	hsv[:,:,n_chnl] = cv2.equalizeHist(hsv[:,:,n_chnl])
	roi = hsv[y:y+h , x:x+w]
	mask = cv2.inRange(roi , np.array((100. , 30. ,32. )) , np.array((180. , 120. , 255. )))
	
	roi_hist = cv2.calcHist([roi] , [n_chnl] ,mask, [180] , [0,180])
	cv2.normalize(roi_hist , roi_hist  , 0,255 , cv2.NORM_MINMAX)
	term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT , 10,1 )

# This function to track the region of interest
def my_meanshift():
 global term_crit , n_chnl , frame , track_window , roi_hist ,hsv,x,y
 hsv = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)
 hsv[:,:,n_chnl] = cv2.equalizeHist(hsv[:,:,n_chnl])
 dst = cv2.calcBackProject([hsv] , [n_chnl] , roi_hist , [ 0,180 ], 1)

 ret , track_window = cv2.meanShift(dst,track_window , term_crit)
 x , y , w , h = track_window
 img = cv2.rectangle(frame , (x,y) , (x+w ,y+h) , 255 , 2)
 return img


f_meanshift = False
n_chnl = 0

# video directory
cap = cv2.VideoCapture('vid.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()
    # Resize frame
    frame = cv2.resize(frame, (900, 600))
    # Image processing part:
    # 1- Polygon region (ROI)
    zero = np.zeros(frame.shape,dtype=np.uint8)
    points = np.array([[(305, 283), (381, 305), (345, 361), (203, 305)]])
    cv2.fillPoly(zero,points,(255,255,255))
    crop_image= cv2.bitwise_and(frame,zero)

    # 2- Threshold : to erase noise
    fg = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
    ret, f_threshol = cv2.threshold(fg, 25, 255, cv2.THRESH_BINARY)
    # 3- Opening : to enlarge vehicle shape
    kernel = np.ones((13, 13), np.uint8)
    opening = cv2.morphologyEx(f_threshol, cv2.MORPH_OPEN, kernel)

    # Detection Part
    fim2, fcontours, fhierarchy = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #cv2.imshow('img1', zero)
    #cv2.imshow('img2', crop_image)
    cv2.imshow('img3', f_threshol)
    cv2.imshow('img4', opening)

    try:
     # Show The White Space Of ROI
     cnt = fcontours[0]
     area = cv2.contourArea(cnt)
     print area
     print str(x)
     # check wither the coming Vehicle in a dangerous distance
     if x <= 230 and x!= 0:
         cv2.putText(frame, " WARNING, Collision Danger ! ", (350, 150), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
         x=0

    except :
        print 'error'
    # check wither there is a Vehicle In The ROI
    if area <= 6500 and a ==0 :
        # Crop The Coming Vehicle Image
        new = frame[259:305,305:381]
        cv2.imshow('img5', new)
        #meanshift
        track_window = (305,259 ,381-305,305-259 )
        f_meanshift = True
        roi_meanshift(frame , n_chnl ,259 , 305-259 , 305 , 381-305)
        a=1

    # if the ROI Got Its Normal Space Again Reset "a" To Receive New Vehicle
    if area > 6740 :
        a =0
        f_meanshift = False

    # change ROI color wither while occupied be coming Vehicle
    f_cc = cv2.drawContours(frame, fcontours, -1, (0, 255, 0), 3)
    if a==1 :
        f_cc = cv2.drawContours(frame, fcontours, -1, (0, 0, 255), 3)
    
    if f_meanshift:
		frame = my_meanshift()

    cv2.imshow('img', frame)
    cv2.waitKey(10)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
