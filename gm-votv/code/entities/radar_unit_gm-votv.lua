--@name RADAR Unit GM-VOTV
--@author Lawman
--@shared

	local radar_speed = 402.0

if SERVER then

	local cpos = chip():getPos()
	local radius = 24000
	local radarTargets = {}
	
	local COLORS = 
	{
		player = Color(255,255,0),
		prop_physics = Color(200,255,200),
		sent_point_beam = Color(255,0,0),
		sent_suspension_spring = Color(0,255,255)
	}

	local validClasses =
	{
		player=true,
		sent_point_beam=true,
		sent_suspension_spring=true
	}

	timer.create("CatchEntities",1,0,function()

		local EntsTable = find.inSphere( cpos,radius,function(ent) return isValid(ent) and validClasses[ent:getClass()] end)
		radarTargets = {}

		for _, v in ipairs(EntsTable) do

			local entPos = v:getPos()

			local dx = entPos.x - cpos.x
			local dy = entPos.y - cpos.y
			local distance = math.sqrt(dx^2 + dy^2)

			local screenRadius = 256
			local scale = screenRadius / radius
			local x = screenRadius + dx * scale
			local y = screenRadius + dy * scale

			table.insert(radarTargets, {
			_x = math.floor(x), 
            _y = math.floor(y),
            class = v:getClass(),
			color = COLORS[v:getClass()] or Color(255,255,255)
        	})

		end

		net.start("RADAR_TARGETS_UPD")
		net.writeTable(radarTargets)
		net.send()
	
	end)

	RadarPing = 0
	RadarActive = true
	timer.create("RadarUpdate", 0.1, 0, function()

		if not RadarActive then return end
		
		if RadarPing < 192 then

			RadarPing = RadarPing + (radar_speed/192)

		else

			RadarPing = 0

			net.start("RadarPingSound")
			net.send()

		end

		net.start("RadarPingUpdate")
		net.writeTable({RadarPing})
		net.send()

	end)

end

if CLIENT then

    local font1 = render.createFont("x14y24pxHeadUpDaisy",24,500,true,false,false,false,0,true,0)
    local font2 = render.createFont("x14y24pxHeadUpDaisy",14,500,true,false,false,false,0,true,0)
	local font3 = render.createFont("x14y24pxHeadUpDaisy",8,500,true,false,false,false,0,true,0)
	
    local r_ping = 0
    local cd = false
    local times_C = 55
	local radar_opac = 0
	local radarTargets = {}

	net.receive("RadarPingUpdate", function()

		local tbl = net.readTable()

		r_ping = tbl[1]
		radar_opac = math.clamp(radar_opac - 1, 0, 255)

	end)
	
	net.receive("RADAR_TARGETS_UPD", function()

		radarTargets = net.readTable()
	
	end)

	net.receive("RadarPingSound", function()

		chip():emitSound("friends/friend_join.wav", 100, 210)
		radar_opac = 255
		times_C = times_C + 1

	end)

    hook.add("Render", "", function() 
        
        local x,y = render.getResolution()
        
        render.setColor(Color(255,255,255))
		render.drawRectOutline( 64, 64, 192*2, 192*2, 1 )
        render.drawCircle( x/2, y/2, 192 )

		
        render.setFont(font1)
            render.drawText( 5 , 5 , "Radar UNIT:" , TEXT_ALIGN.LEFT)
            
            render.setFont(font2)
                render.drawText( 5, 39, "Working Cycles: ~" .. tostring( times_C ), TEXT_ALIGN.LEFT)
                
		render.setColor(Color(255,255,255,5))
        render.drawCircle( x/2, y/2, 172 )
		render.drawCircle( x/2, y/2, 142 )
		render.drawCircle( x/2, y/2, 112 )
		render.drawCircle( x/2, y/2, 92 )
        render.drawCircle( x/2, y/2, 62 )
		render.drawCircle( x/2, y/2, 32 )
		
		for _, v in pairs(radarTargets) do

			local x_,y_,class = v._x,v._y,v.class
			local subColor = Color(0,0,0,0)

			if (x_>380 or x_<-380) or (y_>400 or y_<-400) then

				subColor = Color(0,0,0,240)

			else

				subColor = Color(0,0,0,0)

			end

			local col = v.color	- subColor 

			x_ = math.clamp(x_,-440,440)
			y_ = math.clamp(y_,-440,440)
			render.setColor(col)
			render.drawFilledCircle(x_,y_,2)


			render.setFont(font3)

			render.setColor(col:setA(50))
			render.drawSimpleText(x_,y_, tostring(x_).."/"..tostring(y_))

		end

		            render.setFont(font2)
        
        render.setColor(Color(255,255,255 - (math.clamp( math.sin(timer.curtime())*55, -55 , 0)) ))
        render.drawSimpleText( 10, y-29, "RADAR SPEED: " ..string.format("%.2f", radar_speed/270).." px/s" )
        
        render.setColor(Color(2,255,2, 192 - r_ping))
        render.drawCircle( x/2, y/2, r_ping )
        
    end)
 
end