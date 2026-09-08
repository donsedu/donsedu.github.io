'use strict';

LDR = LDR || {};

LDR.PLIBuilder = function(loader, showEditor, mainModelID, canvas, renderer) {
    this.loader = loader;
    this.showEditor = showEditor;
    this.canvas = canvas;
    this.renderer = renderer;
    this.fillHeight = false;
    this.groupParts = true;
    this.clickMap;

    // Register for options changes:
    let self = this;
    if(LDR.Options) {
        LDR.Options.listeners.push(function() {
                if(self.lastStep) {
                    self.drawPLIForStep(self.fillHeight, self.lastStep,
                                        self.lastMaxWidth, self.lastMaxHeight, 0, true);
                }
            });
    }

    // Set up rendering elements:
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 1000000);
    this.camera.position.set(10000, 7000, 10000);
    this.camera.lookAt(new THREE.Vector3());
    this.measurer = new LDR.Measurer(this.camera);
    this.scene = new THREE.Scene(); // Will only contain one element at a time.
}

LDR.PLIBuilder.prototype.getPartType = function(id) {
    let pt = this.loader.getPartType(id);
    if(!pt.mesh) { // Ensure size is computed.
	pt.mesh = new THREE.Group();
	let opaqueObject = new THREE.Group();
	let sixteenObject = new THREE.Group();
	let transObject = new THREE.Group();
	pt.mesh.add(opaqueObject);
	pt.mesh.add(sixteenObject);
	pt.mesh.add(transObject);

        // Set up mesh collector:
	pt.pliMC = new LDR.MeshCollector(opaqueObject, sixteenObject, transObject);
	let p = new THREE.Vector3();
	let r = new THREE.Matrix3(); r.set(1,0,0, 0,-1,0, 0,0,-1);
	pt.generateThreePart(this.loader, 16, p, r, true, false, pt.pliMC);

        // Draw to ensure bounding box:
        pt.pliMC.draw(false);
	let elementCenter = new THREE.Vector3();
	let b = pt.pliMC.boundingBox;
	b.getCenter(elementCenter);
	pt.mesh.position.sub(elementCenter);

	let [width,height,linesBelow,linesAbove] = this.measurer.measureConvexHull(b, pt.mesh.matrixWorld);
	pt.dx = width;
	pt.dy = height;
        pt.linesBelow = linesBelow;
        pt.linesAbove = linesAbove;
    }
    return pt;
}

LDR.PLIBuilder.prototype.updateCamera = function(w, h) {
    this.camera.left = -w*0.51;
    this.camera.right = w*0.51;
    this.camera.top = h*0.51;
    this.camera.bottom = -h*0.51;
    this.camera.updateProjectionMatrix();
}

LDR.PLIBuilder.prototype.renderIcon = function(partID, c, w, h) {
    let pt = this.getPartType(partID);

    pt.pliMC.overwriteColor(c);
    pt.pliMC.draw(false);

    this.scene.add(pt.mesh);

    this.renderer.setSize(w+1, h+1); // +1 to ensure edges are in frame in case of rounding down.
    this.updateCamera(pt.dx, pt.dy);

    let composer = new THREE.EffectComposer(this.renderer);
    if(pt.pliMC.attachGlowPasses(w, h, this.scene, this.camera, composer)) { 
        composer.addPass(new THREE.RenderPass(this.scene, this.camera));
        composer.render();
    }
    else {
        this.renderer.render(this.scene, this.camera);
    }

    this.scene.remove(pt.mesh);
}

LDR.PLIBuilder.prototype.createClickMap = function(step) {
    let icons = {}; // key -> {key, partID, c, mult, desc}, key='part_id'_'color_id'
    this.clickMap = [];
    for(let i = 0; i < step.subModels.length; i++) {
	let dat = step.subModels[i];
	if(this.groupParts && dat.REPLACEMENT_PLI === true) {
	    continue; // Do not show replaced part.
	}
	let partID = (this.groupParts && dat.REPLACEMENT_PLI) ? dat.REPLACEMENT_PLI : dat.ID;
	let partType = this.loader.getPartType(partID);
        if(!partType) {
            continue; // Part not loaded
        }
	let c = dat.c;
	let key = partID.endsWith('.dat') ? partID.substring(0, partID.length-4) : partID;
	let pliID = key;

	// Check if there is special PLI information for this part:
	if(partType.preview || LDR.PLI && LDR.PLI.hasOwnProperty(pliID)) {
	    partID = "pli_" + partType.ID;
	    if(!this.loader.partTypes.hasOwnProperty(partID)) {
		let r;
		if(partType.preview) {
		    r = partType.preview.r;
		}
		else {
		    r = new THREE.Matrix3();
		    let pliInfo = LDR.PLI[pliID];
		    r.set(pliInfo[0], pliInfo[1], pliInfo[2],
			  pliInfo[3], pliInfo[4], pliInfo[5],
			  pliInfo[6], pliInfo[7], pliInfo[8]);
		}
		let step = new THREE.LDRStep();
		step.addSubModel(new THREE.LDRPartDescription(16, new THREE.Vector3(), r,
							      partType.ID, true, false));
		let pt = new THREE.LDRPartType(); // Potentially rotated PLI.
		pt.ID = partID;
		pt.modelDescription = partType.modelDescription;
		pt.author = partType.author;
		pt.license = partType.license;
		pt.inlined = partType.inlined;
                pt.isPart = partType.isPart;
		pt.steps.push(step);
		this.loader.partTypes[partID] = pt;
	    }
	    dat.ID = partID;
	}

	key += '_' + c;
	let icon = icons[key];
        if(this.groupParts && icon) {
            icon.mult++;
	}
	else {
	    let pt = this.getPartType(partID);
	    let b = pt.pliMC.boundingBox;
	    icon = {key: key,
		    partID: partID,
		    c: c,
                    mult: 1,
		    desc: pt.modelDescription,
		    annotation: LDR.Annotations ? LDR.Annotations[pliID] : null,
		    dx: pt.dx,
		    dy: pt.dy,
                    linesBelow: pt.linesBelow,
                    linesAbove: pt.linesAbove,
		    size: b.min.distanceTo(b.max),
		    inlined: pt.inlined,
                    part: dat, // Used by editor.
		   };
	    icons[key] = icon;
	    this.clickMap.push(icon);
	}
    }

    let sorter = function(a, b) {
        if(a.dx != b.dx) {
            return a.dx < b.dx ? -1 : 1; // Sort by width.
        }

	let ca = a.desc;
	let cb = b.desc;
	if(ca !== cb) {
	    return ca < cb ? -1 : 1; // Group plates, bricks, etc. (Only works well when not also sorting by width above)
	}
	return a.c - b.c;
    }
    this.clickMap.sort(sorter);
}

LDR.PLIBuilder.prototype.drawPLIForStep = function(fillHeight, step, maxWidth, maxHeight, force) {
    let groupParts = !this.showEditor;
    // Ensure no re-draw if not necessary:
    if(!force &&
       this.lastStep && this.lastStep.idx === step.idx && this.groupParts === groupParts &&
       this.lastMaxWidth === maxWidth && this.lastMaxHeight === maxHeight &&
       this.fillHeight === fillHeight) {
	return;
    }

    const LOWER_LIMIT = 10;
    if(maxWidth < LOWER_LIMIT || maxHeight < LOWER_LIMIT) {
        this.canvas.style.display = 'none';
        return;
    }
    this.canvas.style.display = 'inline-block';

    this.groupParts = groupParts;
    this.fillHeight = fillHeight;
    this.lastStep = step;
    this.lastMaxWidth = maxWidth;
    this.lastMaxHeight = maxHeight;

    // Find, sort and set up icons to show:
    this.createClickMap(step);
    let textHeight = (!fillHeight ? maxHeight : maxWidth) / Math.sqrt(this.clickMap.length) * 0.19;
    // 固定字體：不隨零件數/步驟變動（各步驟字體一致）；桌面 20px / 手機 18px
    const baseFont = maxWidth >= 260 ? 20 : 18;
    let [W,H] = Algorithm.PackPlis(fillHeight, maxWidth-4, maxHeight-8, this.clickMap, textHeight);
    const DPR = window.devicePixelRatio;
    // 自動撐開：PackPlis 後每個 icon 位置已定，估算 annotation（長度數字）實際右緣，
    // 需要多少右側空間才撐開 canvas。字元寬用固定 0.62*fontPx（跨瀏覽器一致，
    // Safari/Chrome measureText 差異會造成卡寬不同 → 右側空白不一致）。
    let needW = maxWidth;
    if(fillHeight) {
        const g2d = this.canvas.getContext('2d');
        if(g2d) {
            const fontPx = baseFont*DPR;
            const padX = fontPx*0.2;
            const margin = 2;
            this.clickMap.forEach(icon => {
                if(!icon.annotation) return;
                const tw = icon.annotation.length * fontPx * 0.62;
                const right = (icon.x + icon.FULL_DX + 1)*DPR + tw + padX*2 + margin;
                needW = Math.max(needW, right/DPR);
            });
        }
        needW = Math.ceil(needW);
        let h = Math.max(100, 12+H);
        this.canvas.width = needW*DPR;
        this.canvas.height = h*DPR;
        this.canvas.style.width = needW+"px";
        this.canvas.style.height = h+"px";
    }
    else {
        let w = Math.max(100, 12+W);
        this.canvas.width = w*DPR;
        this.canvas.height = maxHeight*DPR;
        this.canvas.style.width = w+"px";
        this.canvas.style.height = maxHeight+"px";
    }

    let context = this.canvas.getContext('2d');
    if(!context) {
	console.warn('2D context for PLI not yet ready.');
	return;
    }

    const scaleDown = 0.98; // To make icons not fill out the complete allocated cells.
    let self = this;

    context.clearRect(0, 0, context.width, context.height);
    context.translate(6, 6);
    // Draw icon:
    for(let i = 0; i < self.clickMap.length; i++) {
	let icon = self.clickMap[i];
        let x = icon.x*DPR;
        let y = icon.y*DPR;
	let w = parseInt(icon.DX*scaleDown);
	let h = parseInt(icon.DY*scaleDown);
        self.renderIcon(icon.partID, icon.c, w, h);
	context.drawImage(self.renderer.domElement, x, y);
	
        // Hack to ensure it works on Android:
        [w, h] = LDR.getScreenSize();
        this.renderer.setSize(w, h, true);
    }

    // Draw multipliers:
    context.fillStyle = "#000";
    context.lineWidth = "1";
    if(this.groupParts) {
        // 數量字體：固定大小（baseFont），各步驟一致
        context.font = parseInt(baseFont*DPR) + "px sans-serif";
        context.fillStyle = "black";
        function drawMultiplier(icon) {
            let x = icon.x * DPR;
            let y = (icon.y + icon.MULT_Y) * DPR;
            let w = icon.MULT_DX * DPR;
            let h = textHeight * DPR;
            // 數量文字 y 基準：靠近零件下緣（0.92 → 0.72）
            context.fillText(icon.mult + "x", x, y + h*0.72);
        }
        this.clickMap.forEach(drawMultiplier);
    }
    // Draw Annotation:（零件長度文字）
    // 字體固定（baseFont）與數量一致；外框/圓形底以文字實際寬度 + padding 自動調整。
    // 保持在零件右下方：右側預留帶(annotationReserve)已撐開 canvas，末端兜底收進邊界。
    context.font = parseInt(baseFont*DPR) + "px sans-serif";
    this.clickMap.filter(icon => icon.annotation).forEach(icon => {
	let x = (icon.x+icon.FULL_DX+1)*DPR;
	let y = (icon.y+icon.ANNO_Y)*DPR;
	let h = textHeight*DPR;
	const txt = icon.annotation;
	const fontPx = parseInt(baseFont*DPR);
	const tw = context.measureText(txt).width;      // 文字實際寬度
	const padX = fontPx*0.2;                         // 左右 padding（字高 0.2）
	const padY = fontPx*0.2;                         // 上下 padding（字高 0.2）
	const cw = context.canvas.width;
	const ch = context.canvas.height;
	const margin = 2;
	// 兜底：極端長文字若超出右緣則收進邊界（正常由預留帶容納，維持在零件右側）
	const wNeed = tw + padX*2;
	if (x + wNeed + margin > cw) x = cw - wNeed - margin;
	if (x < margin) x = margin;
	// 垂直位置（baseline）：頂/底超出畫布時收進邊界
	let baseY = y + h*0.79;
	if (baseY - fontPx - padY < margin) baseY = fontPx + padY + margin;
	if (baseY + margin > ch) baseY = ch - margin;
	context.beginPath();
	context.fillStyle = "#CFF";
	if(icon.desc && icon.desc.startsWith('Technic Axle')) {
	    // 圓形底：以文字中心為圓心，半徑 = max(文字寬, 字高)/2 + padding
	    const rad = Math.max(tw, fontPx)/2 + padX;
	    let cx = x + tw/2;
	    cx = Math.min(Math.max(cx, rad + margin), cw - rad - margin);
	    const cy = baseY - fontPx*0.45;
	    context.arc(cx, cy, rad, 0, 2*Math.PI, false);
        }
	else {
	    // 方框底：文字寬 + 左右 padding、字高 + 上下 padding
	    context.rect(x - padX, baseY - fontPx - padY, wNeed, fontPx + padY*2);
        }
	context.fill();
	context.stroke();
	context.fillStyle = "#25E";
	context.fillText(txt, x, baseY);
    });
    // Draw highlight for ghosted parts:
    if(this.showEditor) {
        context.strokeStyle = "#5DD";
        context.lineWidth = '4';
	let hoveredIcon = null;
        this.clickMap.forEach(icon => {
            if(icon.part.original.ghost) {
                let x = parseInt((icon.x)*DPR);
                let y = parseInt((icon.y)*DPR);
                let w = parseInt((icon.DX)*DPR);
                let h = parseInt((icon.DY)*DPR);
                context.strokeRect(x, y, w, h);
            }
	    if(icon.part.original.hover) {
		hoveredIcon = icon;
	    }
        });
	if(hoveredIcon) {
	    context.strokeStyle = "#000";
	    context.setLineDash([10, 10]);
	    this.clickMap.forEach(icon => {
                let x = parseInt((hoveredIcon.x)*DPR);
                let y = parseInt((hoveredIcon.y)*DPR);
                let w = parseInt((hoveredIcon.DX)*DPR);
                let h = parseInt((hoveredIcon.DY)*DPR);
                context.strokeRect(x, y, w, h);
            });
	}
    }
}
