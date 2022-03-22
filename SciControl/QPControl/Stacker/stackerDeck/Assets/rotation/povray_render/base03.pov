//
// Kevin Yager
//



// =========================================================
// INCLUDES
// =========================================================

#include "colors.inc"    // The include files contain
#include "stones.inc"    // pre-defined scene elements
#include "textures.inc"  // pre-defined scene elements
#include "shapes.inc"
#include "glass.inc"
#include "metals.inc"
#include "woods.inc"

// #version 3.6

// =========================================================
// RENDER OPTIONS
// =========================================================
//background { color White }

// side_render gives a view from side. Otherwise the angled
// view is used.
#declare side_render = false;


// Determines whether all the "slick" rendering options are enabled 
#declare intense_render = true;




// =========================================================
// LIGHTS
// =========================================================


// General illumination



#declare lighting_spread = 10;
#declare lighting_num = 3;
// Area lighting
light_source { 
        //<65,10,100>
        <65,-20,100>  // for oct
        color rgb 1.0*<1,1,1>
        #if(intense_render)
            area_light
            lighting_spread*<-1,+1,0>,lighting_spread*<-1,-1,1>,lighting_num,lighting_num
        #end
        }
light_source { 
        <150,250,150> 
        color rgb 1.0*<1,1,1>
        #if(intense_render)
            area_light
            lighting_spread*<-1,+1,0>,lighting_spread*<-1,-1,1>,lighting_num,lighting_num
        #end
        }
            



// =========================================================
// CAMERAS
// =========================================================

#declare zoom = 1.0;

// Far-off angle view
#declare angledview =   
        camera {
          location zoom*<0, 90, 110>
          sky <0,0,1>
          look_at  <0, 20, 20>
        }
// Medium angle view
#declare angledview2 =   
        camera {
          location zoom*<70, 60, 30>
          sky <0,0,1>
          look_at  <0, 0, 20>
        }        

// Close angle view
#declare angledview3 =   
        camera {
          location zoom*<20, 40, 30>
          sky <0,0,1>
          look_at  <0, 0, 20>
        }        
        
// Close-up side-on shot
#declare sideview = 
        camera {
          orthographic
          location zoom*<20, 0, 0>
          sky <0,0,1>
          look_at  <0, 0, 0>
        }
// Front view (looking into x)
#declare frontview =
        camera {
          orthographic
          location zoom*<60,0,0>
          sky <0,0,1>
          look_at <0,0,0>
        }        
// Straight top-view
#declare topview =
        camera {
          orthographic
          location zoom*<0,0,150>
          look_at <0,0,0>
        }
// Top-down view of the sample cell (close-up)
// (should be used with top_render = true )
#declare topcellview =
        camera {
          orthographic
          location zoom*<-60,0,40>
          look_at <-60,0,0>
        }





// =========================================================
// TEXTURES
// =========================================================


#declare test_texture = texture { pigment { color Blue } }

#declare matte_black =
        texture{ 
                pigment { color rgb<0.1,0.1,0.1> } 
                finish {
                    phong 0.8
                    specular 0.9
                    crand 0.5
                    diffuse 0.5
                }
        }

#declare OpticalGlass =
    texture { 
        pigment { color rgbf<0.8,0.8,1,0.9> }
        finish {
            reflection 0.1
            refraction 1.0    
            ior 1.4
            phong 0.4
        }
        
    }
#declare Lucite =
    texture { 
        pigment { color rgbf<0.8,0.8,0.8,0.9> }
        finish {
            reflection 0.1
            refraction 1.0    
            ior 1.4
            phong 0.4
        }
        
    }    

#declare dark_metal = texture { 
                pigment { P_Chrome2 }
                finish { F_MetalA }
        }
#declare light_metal = texture { 
                pigment { P_Chrome3 }
                finish { F_MetalA }
        }    


#declare purge_texture = 
        texture { pigment { color rgb<0.627,0.58,0.44> } }
#declare copper_like = texture {
                pigment { P_Copper3 }
                finish { 
                        F_MetalA
                        reflection 0.06
                        crand 0.1
                }
        }


#declare silicon_like = texture {
                pigment { P_Chrome2 }
                finish {
                        F_MetalD                        
                }
        }        
#declare silicon_cartoon = texture {
                pigment { P_Chrome2 }
                finish {
                        F_MetalD                        
                        reflection 0.05
                }
        }        


#declare gold_like = texture {
                T_Gold_1A
                //pigment { color rgb <0.98,0.859,0.376> }
                finish {
                        F_MetalA
                        reflection 0.8
                }       
/*
                T_Gold_1A
                finish { 
                        F_MetalA
                        reflection 0.06
                        crand 0.1
                }
*/                
        }

#declare gold_like2 = texture {
                T_Gold_1A
                //pigment { color rgb <0.98,0.859,0.376> }
                finish {
                        F_MetalA
                        reflection 0.1
                }       
}     
#declare iron_oxide_like = texture {
    pigment { rgb <136/255,56/255,24/255> }
}




// =========================================================
// GUIDES
// =========================================================

// Coordinate guide
#declare axesize = 0.9;
#declare axescylsize = 20;
#declare coordguide = union {
    // Red   = X
    // Green = Y
    // Blue  = Z
    sphere {
      <0, 0, 0>, axesize
      texture {
        pigment { color Yellow }
      }
    }
    cylinder {
      <0,0,0>,<axescylsize*axesize, 0, 0>, axesize/2
      texture {
        pigment { color Red }
      }
    }
    cylinder {
      <0,0,0>,<0, axescylsize*axesize, 0>, axesize/2
      texture {
        pigment { color Green }
      }
    }
    cylinder {
      <0,0,0>,<0, 0, axescylsize*axesize>, axesize/2
      texture {
        pigment { color Blue }
      }
    }
}
//object { coordguide }

// Ruler guide
#declare rulerspacing = 10;
#declare numrulerpoints = 10;
#declare inum = 0;
#declare rulerguide = union {
    #while (inum < numrulerpoints)
        sphere { <0,0,inum*rulerspacing>,axesize/10 }
        #declare inum = inum + 1;
    #end
    texture { pigment { color Blue } }
}
//object { rulerguide }

// Grid guide
#declare gridspacing = 20;
#declare gridpipewidth = 0.2;
#declare numgridels = 5;
#declare inum = -numgridels;
#declare gridhalf = union {
    #while (inum <= numgridels)
        cylinder { 
            <-gridspacing*numgridels,0,0>,<gridspacing*numgridels,0,0>,gridpipewidth
            translate y*inum*gridspacing
        }
        #declare inum = inum + 1;
    #end
   
    texture { pigment { color Grey } } 
}
#declare gridguide = union {
    object { 
        gridhalf 
    }
    object { 
        gridhalf
        rotate z*90
    }
} 
//object { gridguide }



#declare test_sphere = sphere {
        <0,0,0>,10
        texture { test_texture }
}
//object { test_sphere }





// =========================================================
// MACROS
// =========================================================


#macro image_plane (im_filename, im_width, im_height)
    intersection {
        // Create a sheet from <0,0> to <1,1>
        plane {
            <0,0,1>,0
        }
        box {
            <0,0,-0.001>,<+1,+1,-0.001>
        }
        texture {
            pigment {
                image_map {
                    png im_filename
                }
            }
        }
            
        // Move to origin
        translate <-0.5,-0.5,0>
        scale <im_width, im_height,1>
        rotate x*90
        scale 0.05
    }
#end
//image_plane ("GTSAXS_grating03.png", 2200, 1600)
//image_plane ("a.png", 600, 535)





#macro octahedron(sizing)
    intersection {
        
        // TOP HALF
        
        // (+x,+y,+z) face
        plane {
            <+1,+1,+1>,0
            translate x*+sizing
        }
        // (-x,+y,+z) face
        plane {
            <-1,+1,+1>,0
            translate x*-sizing
        }
        // (+x,-y,+z) face
        plane {
            <+1,-1,+1>,0
            translate y*-sizing
        }
        // (-x,-y,+z) face
        plane {
            <-1,-1,+1>,0
            translate y*-sizing
        }
        
        
        // BOTTOM HALF
        // (+x,+y,-z) face
        plane {
            <+1,+1,-1>,0
            translate x*+sizing
        }
        // (-x,+y,-z) face
        plane {
            <-1,+1,-1>,0
            translate x*-sizing
        }
        // (+x,-y,-z) face
        plane {
            <+1,-1,-1>,0
            translate y*-sizing
        }
        // (-x,-y,-z) face
        plane {
            <-1,-1,-1>,0
            translate y*-sizing
        }
            
        
    }
#end
//object { octahedron(1.0) }


// =========================================================
// OBJECTS
// =========================================================




 #declare Ag_texture = texture { pigment { rgb 0.5*<1,1,1> } }
#declare cubeNP = box {
    -1,1
    texture { Ag_texture }
    scale 2
}
#declare sphereNP = sphere {
    <0,0,0>,1
    texture { Ag_texture }
    scale 2.5
}

#declare oct_sizing = 1.0;
#declare octNP = object {
    octahedron(oct_sizing)
    texture { Ag_texture }
    scale 3.5
}

#declare Nanoparticle = object { cubeNP }
#declare Nanoparticle = object { sphereNP }

#declare Nanoparticle = object { 
    octNP
    #declare oct_edge = 2.0*oct_sizing*cos(radians(45));
    #declare oct_corner_to_center = (oct_edge/2.0)/( cos(radians(45)) );
    #declare sideview_angle = degrees( atan( oct_corner_to_center/(oct_edge/2) ) );
    rotate z*-45
//     rotate x*55
    rotate x*(  sideview_angle  )
}




// =========================================================
// SCENE CREATION
// =========================================================




// =========================================================
// WORKING AREA
// =========================================================


// object { test_sphere }

// object { coordguide }
// object { gridguide }
// object { rulerguide }


#declare arrow_width = 6;
#declare arrow_radius = 10;
#declare arrow_thickness = 0.5;
#declare arrow_angle = 30;
#declare arrow_construct = merge {

    // Band
    difference {
        cylinder { <-arrow_width/2,0,0>,<+arrow_width/2,0,0>, arrow_radius }
        cylinder { <-1.01*arrow_width/2,0,0>,<+1.01*arrow_width/2,0,0>, (arrow_radius-arrow_thickness) }
        plane { z, 0 }
        plane { z, 0 rotate x*arrow_angle }
    }
    // Triangle arrow head
    difference {
        box {
            <-arrow_width,-arrow_width,-arrow_thickness>,
            <+arrow_width,+arrow_width,0>
            rotate z*45
        }
        plane { y, 0 }
        scale <0.7,0.7,1>
        rotate x*-90
        translate y*arrow_radius
        rotate x*arrow_angle*1.0001
    }
    
    
    //texture { pigment { rgb <0/255, 255/255, 252/255> } }
    texture { pigment { rgbt <0/255, 255/255, 252/255, 0.25> } }
    //texture { pigment { rgbf <0/255, 255/255, 252/255, 0.3> } }
    
}


// Output final object
union { 

    // Stamp holder (glass slide)
    box {
        <-arrow_width*2.0, -arrow_radius/2, -arrow_thickness*0.5>,
        <+arrow_width*1.5, +arrow_radius/2, +arrow_thickness*0.5>
        texture { pigment { rgb 0.5*<1,1,1> } }
    }

    // Arrow
    object {
        arrow_construct
        
        // + roll
        //translate x*-arrow_width*1.25
        
        // - roll
        //rotate z*180
        //rotate x*12
        translate x*-arrow_width*1.25
        
        // - pitch
        //rotate z*-90
        //rotate y*-5
        //translate x*arrow_width*-1

        // + pitch
        //rotate z*+90
        //rotate y*-15
        //translate x*arrow_width*-1

    }
}



// This camera can be modified at will
#declare zoom = 1.0;
#declare varview =   
        camera {
          location zoom*<25, 60, 40>
          sky <0,0,1>
          look_at  <0, 0, 0>
          angle 35
          
        } 

// Close-up side-on shot
#declare zoom = 1.0;
#declare sideview = 
        camera {
          orthographic
          location zoom*<20, 0, 0>
          sky <0,0,1>
          look_at  <0, 0, 0>
        }
   
camera {
    //angledview
    varview
    //topview
    //sideview
  
    //angledview
    //sideview 
    //topview      
    //frontview
    //varview
  
}




