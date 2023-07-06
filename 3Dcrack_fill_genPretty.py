# dummy fill on 5um grid - protect up to 100um before intersection
# scribes are 200 um large
grid=5
scribe=200
protect=100

import uos
import ujson
Jname=uos.getenv('Jname')
f=open(Jname,"r")
lstRef=ujson.load(f)
f.close()

# list of replacing cells used with run==0 -> +15 = backside fill -> used with run==1
# 1 square2.5.gds		
# 2 Hseg.gds		17 HsegB.gds
# 3 Vseg.gds		18 VsegB.gds
# 4 URcorner.gds		19 URcornerB.gds
# 5 ULcorner.gds		20 ULcornerB.gds
# 6 BLcorner.gds		21 BLcornerB.gds
# 7 BRcorner.gds		22 BRcornerB.gds
# 8 Uend.gds		23 UendB.gds
# 9 Rend.gds		24 RendB.gds
# 10 Bend.gds		25 BendB.gds
# 11 Lend.gds		26 LendB.gds
# 12 cross.gds		27 crossB.gds
# 13 RT.gds			28 RTB.gds
# 14 UT.gds			29 UTB.gds
# 15 LT.gds			30 LTB.gds
# 16 BT.gds			31 BTB.gds

HSEG=2
VSEG=3
UR=4
UL=5
BL=6
BR=7
UEND=8
REND=9
BEND=10
LEND=11
CROSS=12
RT=13
UT=14
LT=15
BT=16

def NewRef():
    global DX
    global DY
    global RefCell
    global step
    
    for col in range(colmin,colmax+1):
        for row in range(rowmin,rowmax+1):
            if col%2==ColEven and row%2==RowEven and MAP.array[col,row].value==1:
                RefCell=MAP.array[col,row]
                #print("New reference")
                DX,DY=DY,-DX
                step=0
                return True
    #print("No more point")
    return False


def doPretty(base):
    ENWS={'00XX':UR+base,'XX00':BL+base,'0XX0':BR+base,'X00X':UL+base,\
          '000X':UEND+base,'00X0':REND+base,'0X00':BEND+base,'X000':LEND+base,\
          '0X0X':VSEG+base,'X0X0':HSEG+base,'XXXX':CROSS+base,\
          '0XXX':RT+base,'X0XX':UT+base,'XX0X':LT+base,'XXX0':BT+base}
    
    for col in range(colmin,colmax+1):
      for row in range(rowmin,rowmax+1):
          if MAP.array[col,row].value>=2+base and MAP.array[col,row].value<17+base:
              if col<MAP.width-1 and MAP.array[col+1,row].value>=2+base and MAP.array[col+1,row].value<17+base:
                  codeE='X'
              else:
                  codeE='0'
              if col>0 and MAP.array[col-1,row].value>=2+base and MAP.array[col-1,row].value<17+base:
                  codeW='X'
              else:
                  codeW='0'
              if row<MAP.height-1 and MAP.array[col,row+1].value>=2+base and MAP.array[col,row+1].value<17+base:
                  codeN='X'
              else:
                  codeN='0'
              if row>0 and MAP.array[col,row-1].value>=2+base and MAP.array[col,row-1].value<17+base:
                  codeS='X'
              else:
                  codeS='0'
              MAP.array[col,row].value=ENWS.get(codeE+codeN+codeW+codeS,1)


def validCell(ldx,ldy):
    return (RefCell.col+2*ldx<=colmax and RefCell.row+2*ldy<=rowmax and RefCell.col+2*ldx>=colmin and RefCell.row+2*ldy>=rowmin and MAP.array[RefCell.col+ldx,RefCell.row+ldy].value==1 and MAP.array[RefCell.col+2*ldx,RefCell.row+2*ldy].value==1)


# we move along the direction 'E', 'N', 'W' or 'S' starting from reference point
# Identify reference cell = corner of each chip within matrix or MPW
for point in lstRef:
    # define work area
    if point['P']=='BR':
        RefCell=MAP.cell(point['X']+2*grid/3,point['Y']-2*grid/3)
        colmin=max(0,int(RefCell.col-protect/grid))
        colmax=min(int(RefCell.col+scribe/2/grid),MAP.width-1)
        rowmax=min(int(RefCell.row+protect/grid),MAP.height-1)
        rowmin=max(0,int(RefCell.row-scribe/2/grid))
    elif point['P']=='UL':
        RefCell=MAP.cell(point['X']-2*grid/3,point['Y']+2*grid/3)
        colmin=max(0,int(RefCell.col-scribe/2/grid))
        colmax=min(int(RefCell.col+protect/grid),MAP.width-1)
        rowmax=min(int(RefCell.row+scribe/2/grid),MAP.height-1)
        rowmin=max(0,int(RefCell.row-protect/grid))
    elif point['P']=='UR':
        RefCell=MAP.cell(point['X']+2*grid/3,point['Y']+2*grid/3)
        colmin=max(0,int(RefCell.col-protect/grid))
        colmax=min(int(RefCell.col+scribe/2/grid),MAP.width-1)
        rowmax=min(int(RefCell.row+scribe/2/grid),MAP.height-1)
        rowmin=max(0,int(RefCell.row-protect/grid))
    elif point['P']=='BL':
        RefCell=MAP.cell(point['X']-2*grid/3,point['Y']-2*grid/3)
        colmin=max(0,int(RefCell.col-scribe/2/grid))
        colmax=min(int(RefCell.col+protect/grid),MAP.width-1)
        rowmax=min(int(RefCell.row+protect/grid),MAP.height-1)
        rowmin=max(0,int(RefCell.row-scribe/2/grid))
    
    ColEven=RefCell.col%2
    RowEven=RefCell.row%2
    MaxStep=8
    
    DX=1
    DY=0
    step=0
    finished=not NewRef()
    
    while not finished:
        if step<MaxStep: 
            step+=1
            MAP.array[RefCell.col,RefCell.row].value=2    # mark ref cell for side A
        else:
            step=0    
        if validCell(DX,DY):
            # go forward -> new ref cell 2 steps ahead, mark intermediate cell
            MAP.array[RefCell.col+DX,RefCell.row+DY].value=2
            RefCell=MAP.array[RefCell.col+2*DX,RefCell.row+2*DY]
        elif validCell(DY,-DX):
            DX,DY=DY,-DX    # turn right 
        elif validCell(-DY,DX):
            DX,DY=-DY,DX    # turn left 
        else:
            finished=not NewRef()
    
    doPretty(0)    
    for col in range(colmin,colmax+1):
      for row in range(rowmin,rowmax+1):
          if MAP.array[col,row].value==1:
               MAP.array[col,row].value=17
    doPretty(15)
	   

