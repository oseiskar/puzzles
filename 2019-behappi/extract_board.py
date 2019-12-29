import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input_image')
    p.add_argument('output_image', nargs='?')
    p.add_argument('output_csv', nargs='?')
    return p.parse_args()

args = parse_args()

def downsize(orig_size, max_width=1280):
    w, h = orig_size[:2]
    w1 = max_width
    h1 = int(w1 * w / h)
    return (w1, h1)

img = cv2.imread(args.input_image)
img = cv2.resize(img, downsize(img.shape), cv2.INTER_AREA)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

def np_fftconvolve(A, B):
    # https://laurentperrinet.github.io/sciblog/posts/2017-09-20-the-fastest-2d-convolution-in-the-world.html
    from numpy.fft  import fft2, ifft2
    return np.real(ifft2(fft2(A)*fft2(B, s=A.shape)))

def convolve_image(gray):
    #gray = 255-gray
    gray = cv2.Canny(gray,50,150,apertureSize = 3)

    angle = np.pi/180*50

    kernel_w = 10
    kernel_coord = np.arange(-kernel_w, kernel_w+1)/float(kernel_w)

    kx = kernel_coord[np.newaxis,:]
    ky = kernel_coord[:,np.newaxis]
    kernel_r = np.sqrt(kx**2 + ky**2)
    sa = 0.1
    sb = 1.5
    kernel = np.exp(-0.5*((np.cos(angle) * kx + np.sin(angle) * ky)**2 / sa**2 + kernel_r / sb**2))
    kernel = kernel * (kernel_r <= 1.0)
    kernel = kernel / np.sum(kernel)
    #kernel = kernel*255

    #plt.imshow(kernel)
    #plt.show()

    return np_fftconvolve(gray, kernel)

def my_line_transform(gray, angle_resolution=np.pi/180.0, x_resolution=1.0):
    angle = 0 #np.pi/10
    outimg = cv2.cvtColor(gray*0, cv2.COLOR_GRAY2BGR)

    #np.cos(angle) * x + np.sin(angle) = rho
    #x = (rho - np.sin(angle) * x) / np.cos(angle) = rhop - np.tan(angle)*x

    t = np.tan(angle)
    #offs = 100
    y = np.arange(gray.shape[0])

    for offs in range(100, 200)[::10]:
        x = (offs - t*y).astype(int)
        for i in range(len(x)):
            xx = x[i]
            if xx >= 0 and xx <= gray.shape[1]:
                outimg[y[i], x[i]] = 255

    return outimg

def hough_lines(gray):
    edges = cv2.Canny(gray,50,150,apertureSize = 3)

    #t0 = 100
    #coeff = 2
    #t1 = int(255/coeff)
    #edges = np.minimum(np.maximum((255-gray), t0) - t0, t1)*coeff

    #outimg = img
    outimg = edges
    outimg = cv2.cvtColor(outimg, cv2.COLOR_GRAY2BGR)

    lines = cv2.HoughLines(edges,1,np.pi/180, 30)
    if lines is None: lines = []
    lines = lines[:30]
    for l in lines:
        for rho,theta in l:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(outimg,(x1,y1),(x2,y2),(0,0,255),1)
    return outimg

def corners(gray, max_corners=1500):
    outimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    corners = cv2.goodFeaturesToTrack(gray, max_corners, 0.01, 10)
    corners = np.int0(corners)

    for i in corners:
        x,y = i.ravel()
        cv2.circle(outimg, (x,y), 3, (0,0,255), 2)

    return outimg

def initial_hexgrid_slower(cc, thickness=0.3):
    best_score = 0
    best_mask = None
    for c in cc:
        x0 = np.real(c)
        y0 = np.imag(c)

        d = np.abs(cc - c)
        closest = np.argsort(d)
        for c2 in cc[closest[1:5]]:
            s = np.abs(c-c2)
            angle_u = np.angle(c-c2)
            #score = 0
            #for c3 in cc:
            #    score += mask[int(np.imag(c3)), int(np.real(c3))]
            grid = HexGrid(x0, y0, angle_u, s)
            score = np.sum(grid.evaluate(cc, thickness))
            if score > best_score:
                best_score = score
                best_mask = grid
                print('best score %g/%d' % (score, len(cc)))
    return best_mask

def corners_hex(gray, max_corners=200):
    #outimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    corners = cv2.goodFeaturesToTrack(gray, max_corners, 0.01, 10)
    if corners is None: return gray
    cc = corners[:,0,0]+corners[:,0,1]*1j

    thickness = 0.3
    best_mask = initial_hexgrid_slower(cc, thickness)

    best_mask = best_mask.draw(gray, thickness=thickness)
    outimg = gray * (1.0-best_mask) + best_mask*128
    return outimg

cmplxdot = lambda p, q: np.real(p)*np.real(q) + np.imag(p)*np.imag(q)

class HexGrid:
    def __init__(self, x0, y0, angle, s):
        self.x0 = x0
        self.y0 = y0
        self.angle = angle
        self.scale = s

    @property
    def angle_u(self): return self.angle

    @property
    def angle_v(self): return self.angle + np.pi / 3 * 2

    @property
    def angle_w(self): return self.angle + np.pi / 3 * 4

    @property
    def u_vec(self): return np.exp(1j*self.angle_u)

    @property
    def v_vec(self): return np.exp(1j*self.angle_v)

    @property
    def w_vec(self): return np.exp(1j*self.angle_w)

    def perp_basis(self, dual=False):
        pb = np.array([self.u_vec, self.v_vec])
        if dual: pb *= 1j
        return pb

    def basis(self, dual=False):
        if dual:
            s = self.s2h
        else:
            s = 2
        return self.perp_basis(dual)*1j*s

    def origin(self, dual=False):
        if dual: return 0
        pb = self.perp_basis(dual)
        return (pb[0] + pb[1]) * self.s2h

    @property
    def s2h(self): return 2 / np.sqrt(3)

    def unscaled_xy(self, xy):
        return (xy - (self.x0 + self.y0*1j)) / self.scale

    def scaled_xy(self, xy):
        return xy * self.scale + self.x0 + self.y0*1j

    def img2xy(self, gray):
        x = np.arange(gray.shape[1])[np.newaxis, :]
        y = np.arange(gray.shape[0])[:, np.newaxis]
        xy = x + 1j*y
        return xy

    def draw(self, gray, **kwargs):
        return self.evaluate(self.img2xy(gray), **kwargs)

    def draw_coord(self, gray, dual=False):
        outimg = np.zeros(gray.shape[:2] + (3,), np.uint8)
        xy = self.img2xy(gray)
        coords, centers = self.coord(xy, dual=dual)
        to_col = lambda x: (((x % 256)*31) % 256).astype(np.uint8)
        outimg[:,:,0] = to_col(np.real(coords))
        outimg[:,:,1] = to_col(np.imag(coords))
        outimg[:,:,2] = np.abs(xy - centers)*10
        return outimg

    def evaluate(self, xy, thickness=0.1):
        xy = self.unscaled_xy(xy)
        score = np.real(xy*0)

        coords = []
        for vec in [self.u_vec, self.v_vec, self.w_vec]:
            perp = vec * 1j
            c = cmplxdot(vec, xy)*np.sqrt(3)*0.5
            c_perp = cmplxdot(perp, xy)
            perp_coord = np.round(c_perp)
            coord = np.floor(c + (perp_coord % 2)*1.5).astype(int)
            is_edge = np.abs(c_perp - perp_coord) < thickness*0.5
            score = np.maximum(score, is_edge & (coord % 3 == 0))

        return score

    def coord2img(self, uv):
        b = self.basis()
        return self.scaled_xy(self.origin() + b[0]*np.real(uv) + b[1]*np.imag(uv))

    def coord(self, xy, dual=False):
        xy = self.unscaled_xy(xy)

        perp_basis = self.perp_basis(dual)
        basis = self.basis(dual)
        origin = self.origin(dual)

        M = [np.real(basis), np.imag(basis)]
        xy_flat = np.ravel(xy - origin)
        rhs = [np.real(xy_flat), np.imag(xy_flat)]
        uv = np.linalg.solve(M, rhs)
        uv = (uv[0, :] + 1j*uv[1, :]).reshape(xy.shape)
        center0 = np.round(uv)
        best_dists = None
        best_coords = None
        nearest_center_coords = None

        for du in range(-1,2):
            for dv in range(-1,2):
                center1 = center0 + (du + 1j*dv)
                center1_xy = np.real(center1)*basis[0] + np.imag(center1)*basis[1] + origin
                dists = np.abs(center1_xy - xy)
                if best_dists is None:
                    best_coords = center1
                    best_dists = dists
                    nearest_center_coords = center1_xy
                else:
                    is_best = dists < best_dists
                    if dual:
                        is_best = is_best & (np.round(np.real(center1) + np.imag(center1)).astype(int) % 3 != 1)
                    best_dists[is_best] = dists[is_best]
                    best_coords[is_best] = center1[is_best]
                    nearest_center_coords[is_best] = center1_xy[is_best]

        return best_coords, self.scaled_xy(nearest_center_coords)

    def set_displacement_field(self, xy0, xy1):
        coord, _ = self.coord(xy1)
        u = np.real(coord)
        v = np.imag(coord)
        margin = 4
        minmax = lambda arr: (int(np.min(arr) - margin), int(np.max(arr) + margin))
        self.min_u, self.max_u = minmax(np.real(coord))
        self.min_v, self.max_v = minmax(np.imag(coord))
        self.image_grid = np.zeros((self.max_u - self.min_u + 1, self.max_v - self.min_v + 1))*1j*0

        for u in range(self.min_u, self.max_u+1):
            for v in range(self.min_v, self.max_v+1):
                pix = self.coord2img(u + v*1j)
                closest = np.argsort(np.abs(xy1 - pix))[:6]
                d = np.mean(xy0[closest] - xy1[closest])
                self.image_grid[u - self.min_u, v - self.min_v] = d + pix

    def elements(self):
        for u in range(self.min_u, self.max_u+1):
            for v in range(self.min_v, self.max_v+1):
                uv = u + v*1j
                pix = self.coord2img(uv)
                yield(uv, self.image_grid[u - self.min_u, v - self.min_v], pix)

def initial_hexgrid_fast(cc):
    dists = []
    angles = []

    for c in cc:
        x0 = np.real(c)
        y0 = np.imag(c)
        deltas = cc - c
        d = np.abs(deltas)
        d[d < 1e-6] = 1e10
        best = np.argmin(d)
        dists.append(d[best])
        a = np.fmod(np.angle(deltas[best]) + 2*np.pi, 2*np.pi/3)
        angles.append(a)

    def ransac(arr, thr):
        best_inliers = []
        for x in arr:
            inliers = [y for y in arr if abs(x-y) < thr]
            if len(inliers) > len(best_inliers):
                best_inliers = inliers
        return np.mean(best_inliers)


    angVecs = [np.exp(3j*a) for a in angles]
    angle_u = np.angle(ransac(angles, np.pi/180*10))/3

    midpoint = np.mean(cc)
    anchor_index = np.argmin(np.abs(midpoint - cc))
    center = cc[anchor_index]
    x0, y0 = np.real(center), np.imag(center)

    #s = ransac(dists, np.median(dists)*0.1)
    s = np.median(dists)

    return HexGrid(x0, y0, angle_u, s)

def fit_displacement_field(grid, cc):
    anchor_index = np.argmin(np.abs(cc - (grid.x0 + grid.y0*1j)))
    _, nearest = grid.coord(cc, dual=True)
    cc1 = nearest
    is_placed = np.zeros(cc.shape, dtype=bool)
    is_placed[anchor_index] = True
    dist_mat = np.abs(cc[:, np.newaxis] - cc[np.newaxis, :])

    while np.sum(~is_placed) > 0:
        dist_to_placed = np.min(dist_mat[:, is_placed], axis=1)
        dist_to_placed[is_placed] = 1e10
        dist_to_placed[dist_to_placed < grid.scale * 0.7] = grid.scale * 2
        next_idx = np.argmin(dist_to_placed)

        dist_to_placed = dist_mat[next_idx, :]*1
        dist_to_placed[~is_placed] = 1e10

        #ref_point = np.argmin(dist_to_placed)
        ref_points = np.argsort(dist_to_placed)[:5]
        ref_displ = np.mean(cc1[ref_points] - cc[ref_points])

        _, nearest = grid.coord(np.array([cc[next_idx]+ref_displ]), dual=True)
        cc1[next_idx] = nearest
        is_placed[next_idx] = True

    cc2 = cc1[:]
    displacements = cc1 - cc
    rang = np.arange(len(cc))
    for j in rang:
        neigh = [n for n in np.argsort(dist_mat[j, :])[:5] if n != j]
        new_displ = np.mean(displacements[neigh])
        _, nearest = grid.coord(np.array([cc[j]+new_displ]), dual=True)
        cc2[j] = nearest

    return cc2

def find_grid(gray, max_corners=1500, visualize=True):
    print('GFTT')
    corners = cv2.goodFeaturesToTrack(gray, max_corners, 0.01, 10)
    if corners is None: return gray
    cc = corners[:,0,0]+corners[:,0,1]*1j

    print('initial hexgrid')
    grid = initial_hexgrid_fast(cc)
    #grid = initial_hexgrid_slower(cc)

    print('fitting displacement field')
    cc1 = fit_displacement_field(grid, cc)

    if visualize:
        print('visu')

        # visualize
        best_mask = grid.draw(gray)[..., np.newaxis]

        #outimg = grid.draw_coord(gray)
        outimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        outimg = outimg * (1.0-best_mask) + best_mask*128
        #outimg = cv2.cvtColor(outimg.astype(np.uint8), cv2.COLOR_GRAY2BGR)

        cmplx_to_pix = lambda c: (int(np.real(c)), int(np.imag(c)))
        for j in range(len(cc)):
            p0, p1 = [cmplx_to_pix(a[j]) for a in [cc, cc1]]
            cv2.circle(outimg, p0, 3, (0,0,255), 1)
            cv2.circle(outimg, p1, 3, (255,0,255), 1)
            cv2.line(outimg, p0, p1, (0, 0, 255))

    print('interpolating displacement field')
    grid.set_displacement_field(cc, cc1)

    if visualize:
        print('visu')
        for uv, img, undistorted in grid.elements():
            p0, p1 = [cmplx_to_pix(a) for a in [img, undistorted]]
            cv2.line(outimg, p0, p1, (0, 255, 255))
    else:
        outimg = None

    return grid, outimg

def tiled_hough_lines(gray):
    h, w = gray.shape
    #edges = gray #255 - gray
    #edges = cv2.Canny(gray,50,150,apertureSize = 3)

    #outimg = edges
    outimg = gray*0 #cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    nx = 3*2 #4
    ny = 4*2 #4
    tx = w // nx
    ty = h // ny

    for iy in range(ny):
        sy = slice(iy*ty, (iy+1)*ty)
        for ix in range(nx):

            #if iy < 4 or ix < 2: continue

            sx = slice(ix*tx, (ix+1)*tx)
            #outimg[sy, sx] = hough_lines(gray[sy, sx])
            #radon_transform(gray[sy, sx])
            outimg[sy, sx] = corners_hex(gray[sy, sx])

    return outimg

def radon_transform(image):
    #image = cv2.Canny(image, 50, 150, apertureSize = 3)
    #image = 255-image

    t0 = 100
    coeff = 2
    t1 = int(255/coeff)
    image = np.minimum(np.maximum((255-image), t0) - t0, t1)*coeff

    plt.imshow(image)
    plt.show()

    from skimage.transform import radon
    theta = np.linspace(0., 180., max(image.shape), endpoint=False)
    sinogram = radon(image, theta=theta, circle=False)

    sinogram = sinogram**2
    w = sinogram.shape[1]
    b = w//3
    w23 = 2*w//3
    result = sinogram[:, :b] + sinogram[:, b:(2*b)] + sinogram[:, w23:(w23+b)]

    b = result.shape[0]//10
    p = []
    for i in range(10):
        sc = result[(i*b):((i+1)*b),:]
        sc = np.max(sc, axis=0)
        if i == 0:
            p = sc
        else:
            p += sc


    #result = sinogram**2
    #for th in range(sinogram.shape[1]):
    #    result[th] =

    plt.imshow(result)
    plt.show()

    #p = np.max(result, axis=0)
    plt.plot(p)
    plt.show()

    return sinogram

def segmentation(gray):
    #thr, binary = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    #binary = (gray > 140) * 255

    binary = cv2.adaptiveThreshold(gray,255,\
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,201, 20)

    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations = 2)

    #dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    #dist_threshold = 3
    #_, foreground = cv2.threshold(dist_transform, dist_threshold, 255, 0)
    #return foreground

    #_, markers = cv2.connectedComponents(foreground)
    _, markers = cv2.connectedComponents(opening)
    #print(ret)
    #print(markers.shape)
    #print(np.unique(np.ravel(markers)))

    min_w = gray.shape[0] * 0.05
    max_w = gray.shape[0] * 0.5

    for m in np.unique(np.ravel(markers)):
        match = markers == m
        projx = np.max(match, axis=0)
        projy = np.max(match, axis=1)
        xwidth = np.sum(projx)
        ywidth = np.sum(projy)
        w = max(xwidth, ywidth)
        touches_border = projx[0] or projx[-1] or projy[0] or projy[-1]
        if w < min_w or w > max_w or touches_border:
            markers[match] = 0

    """
    for itr in range(3):
        bg = markers == 0
        for m in np.unique(np.ravel(markers)):
            if m == 0: continue
            match = markers == m
            match = cv2.dilate(match.astype(np.uint8), kernel, iterations=1)
            markers[match.astype(bool) & bg] = m
    """

    grid, _ = find_grid(gray, max_corners=1500)
    outimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    markercolors = cv2.applyColorMap(((markers * 17) % 256).astype(np.uint8), cv2.COLORMAP_JET)

    markermap = {}
    board = []
    for uv, pix, undistorted in grid.elements():
        x = int(np.real(pix))
        y = int(np.imag(pix))
        if y < 0 or x < 0 or x >= outimg.shape[1] or y >= outimg.shape[0]:
            continue
        marker = markers[y, x]
        if marker == 0: continue
        if marker not in markermap: markermap[marker] = len(markermap)+1
        board.append({
            'u': int(np.real(uv)),
            'v': int(np.imag(uv)),
            'label': markermap[marker],
            'pixel_x': x,
            'pixel_y': y
        })
        col = tuple([int(c) for c in markercolors[y, x, :]])
        cv2.circle(outimg, (x, y), 5, col, -1)

    minu = min([r['u'] for r in board])
    minv = min([r['v'] for r in board])
    for r in board:
        r['u'] -= minu
        r['v'] -= minv

    return board, outimg

    #return cv2.applyColorMap(((markers * 17) % 256).astype(np.uint8), cv2.COLORMAP_JET)
    #return (markers == 22) * 255

    #d = cv2.distanceTransform((markers == 23).astype(np.uint8), cv2.DIST_L2, 5)
    #return (d / d.max())*255

    #return corners_hex((markers == 23).astype(np.uint8) * 255, max_corners=100)
    #return faster_corners_hex((markers == 23).astype(np.uint8) * 255, max_corners=100)

    #return binary

#outimg = hough_lines(gray)
#outimg = radon_transform(gray)
#outimg = tiled_hough_lines(gray)
#outimg = my_line_transform(gray)
#outimg = convolve_image(gray)
#outimg = corners(gray)
#outimg = corners_hex(gray, max_corners=1500)
#grid, outimg = find_grid(gray, max_corners=1500)
board, outimg = segmentation(gray)

if args.output_image is not None:
    cv2.imwrite(args.output_image, outimg)

if args.output_csv is not None:
    import csv
    with open(args.output_csv, 'wt') as f:
        out = csv.DictWriter(f, fieldnames=['u', 'v', 'label', 'pixel_x', 'pixel_y'])
        out.writeheader()
        for row in board: out.writerow(row)
