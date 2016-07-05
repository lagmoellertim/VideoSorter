from guessit import guessit
import tvdb_api as tvdb


import configparser
import os
import shutil
import ui
import sys
import time
import requests
import simplejson
import signal

class videosorter:
    def __init__(self,configFileName='config.txt'):
        self.ui = ui.ui()
        try:
            self.ui.run()
        except:
            self.ui.textMode = True
            self.ui.run()
        signal.signal(signal.SIGINT, self.ui.close)
        self.isRunnable = False
        self.config = configparser.ConfigParser()
        self.configFileName = configFileName
        if os.path.isfile(self.configFileName) == False:

            self.setup()

        else:

            try:
                self.config.read(self.configFileName)
                if os.path.isdir(self.config['Folder Settings']['unsortedfolder']) == False:
                    os.mkdir(self.config['Folder Settings']['unsortedfolder'])
                if len(self.config['API Settings']['apikey']) == 32 and self.config['API Settings']['apikey'] != '' and self.config['API Settings']['apikey'] != '[Enter your TMDB API Key here]':
                    self.isRunnable = True
                    self.tvdbsearch = tvdb.Tvdb(language=self.config['API Settings']['language'])
                else:
                    self.ui.informationDialog('API Key','You need a TMDB API Key to use this programm. You can enter the key in the file {}.'.format(self.configFileName))
            except KeyError:
                self.setup()
            except configparser.ParsingError:
                self.setup()


    def run(self):
        try:
            videos = self.searchVideoFiles(self.config['Folder Settings']['unsortedfolder'])

            currentVideoCount = 0

            for video in videos:
                currentVideoCount += 1
                if self.ui.stop == True:
                    break
                guessitString = video.replace(self.config['Folder Settings']['unsortedfolder'],'').lower().replace('\\',' ').replace('/',' ').replace('-',' ')
                for pair in self.config['Series Settings']['words_to_replace'].split(","):
                    if ":" in pair:
                        guessitString = guessitString.replace(pair.split(":")[0].lower(),pair.split(":")[1].lower())
                guessitData = guessit(guessitString)
                try:
                    tmdbData = self.searchTMDB(guessitData['title'])

                    self.ui.addText('{}/{} {}'.format(currentVideoCount,len(videos),video))

                    if guessitData['type'] == 'episode' and tmdbData['media_type'] == 'tv':
                        if 'season' in guessitData and 'episode' in guessitData:
                            try:
                                tvdbData = self.tvdbsearch[self.filterString(tmdbData['name'])][guessitData['season']][guessitData['episode']]['episodename']
                                self.series_handler(guessitData,tmdbData,video,tvdbData=tvdbData)
                            except:
                                self.series_handler(guessitData,tmdbData,video)
                    else:
                        self.movie_handler(tmdbData,video)

                except IndexError:
                    self.videoNotFound(video)


            if len(videos) == 0:
                self.ui.addText('No video files found')

            if self.config['Folder Settings']['clean_unsorted_folder_after_sorted'] == 'True':
                if len(self.searchVideoFiles(self.config['Folder Settings']['unsortedfolder'])) == 0:
                    self.ui.addText('Cleaning Folder {} ...'.format(self.config['Folder Settings']['unsortedfolder']))
                    shutil.rmtree(self.config['Folder Settings']['unsortedfolder'])
                    os.mkdir(self.config['Folder Settings']['unsortedfolder'])
        except KeyError:
            self.setup()
    def setup(self):
        try:
            self.config.read(self.configFileName)
            if len(self.config['API Settings']['apikey']) == 32 and self.config['API Settings']['apikey'] != '' and self.config['API Settings']['apikey'] != '[Enter your TMDB API Key here]':
                apiKey = self.config['API Settings']['apikey']
        except:
            apiKey = '[Enter your TMDB API Key here]'

        self.config['API Settings'] = {'apikey':apiKey,
                                       'language':'de'}
        self.config['Folder Settings'] = {'moviefolder':'Movies',
                                          'seriesfolder':'Series',
                                          'seasonfolder':'Season',
                                          'episodefolder':'Episode',
                                          'unsortedfolder':'Unsorted',
                                          'clean_unsorted_folder_after_sorted':'True'}
        self.config['Movie Settings'] = {'movie_in_additional_folder':'True'}
        self.config['Series Settings'] = {'episode_in_additional_folder':'True',
                                          'words_to_replace':'',
                                          'episode_number_length':'2',
                                          'movie_in_additional_folder':'True'}

        configFile = open(self.configFileName,'w+')
        self.config.write(configFile)
        configFile.close()

        self.config.read(self.configFileName)

        self.ui.informationDialog('Configuration Error','A Problem with the configuration file was reconized. The file has been reset.')

        try:
            if os.path.isdir(self.config['Folder Settings']['unsortedfolder']) == False:
                os.mkdir(self.config['Folder Settings']['unsortedfolder'])

        except IndexError:
            self.setup()

        sys.exit()

    def isVideoFile(self,filename):
        videoFileExtensions = (
            '264', '3g2', '3gp', '3gp2', '3gpp', '3gpp2', '3mm', '3p2', '60d', '787', '89', 'aaf', 'aec', 'aep', 'aepx',
            'aet', 'aetx', 'ajp', 'ale', 'am', 'amc', 'amv', 'amx', 'anim', 'aqt', 'arcut', 'arf', 'asf', 'asx', 'avb',
            'avc', 'avd', 'avi', 'avp', 'avs', 'avs', 'avv', 'axm', 'bdm', 'bdmv', 'bdt2', 'bdt3', 'bik', 'bin', 'bix',
            'bmk', 'bnp', 'box', 'bs4', 'bsf', 'bvr', 'byu', 'camproj', 'camrec', 'camv', 'ced', 'cel', 'cine', 'cip',
            'clpi', 'cmmp', 'cmmtpl', 'cmproj', 'cmrec', 'cpi', 'cst', 'cvc', 'cx3', 'd2v', 'd3v', 'dat', 'dav', 'dce',
            'dck', 'dcr', 'dcr', 'ddat', 'dif', 'dir', 'divx', 'dlx', 'dmb', 'dmsd', 'dmsd3d', 'dmsm', 'dmsm3d', 'dmss',
            'dmx', 'dnc', 'dpa', 'dpg', 'dream', 'dsy', 'dv', 'dv-avi', 'dv4', 'dvdmedia', 'dvr', 'dvr-ms', 'dvx', 'dxr',
            'dzm', 'dzp', 'dzt', 'edl', 'evo', 'eye', 'ezt', 'f4p', 'f4v', 'fbr', 'fbr', 'fbz', 'fcp', 'fcproject',
            'ffd', 'flc', 'flh', 'fli', 'flv', 'flx', 'gfp', 'gl', 'gom', 'grasp', 'gts', 'gvi', 'gvp', 'h264', 'hdmov',
            'hkm', 'ifo', 'imovieproj', 'imovieproject', 'ircp', 'irf', 'ism', 'ismc', 'ismv', 'iva', 'ivf', 'ivr', 'ivs',
            'izz', 'izzy', 'jss', 'jts', 'jtv', 'k3g', 'kmv', 'ktn', 'lrec', 'lsf', 'lsx', 'm15', 'm1pg', 'm1v', 'm21',
            'm21', 'm2a', 'm2p', 'm2t', 'm2ts', 'm2v', 'm4e', 'm4u', 'm4v', 'm75', 'mani', 'meta', 'mgv', 'mj2', 'mjp',
            'mjpg', 'mk3d', 'mkv', 'mmv', 'mnv', 'mob', 'mod', 'modd', 'moff', 'moi', 'moov', 'mov', 'movie', 'mp21',
            'mp21', 'mp2v', 'mp4', 'mp4v', 'mpe', 'mpeg', 'mpeg1', 'mpeg4', 'mpf', 'mpg', 'mpg2', 'mpgindex', 'mpl',
            'mpl', 'mpls', 'mpsub', 'mpv', 'mpv2', 'mqv', 'msdvd', 'mse', 'msh', 'mswmm', 'mts', 'mtv', 'mvb', 'mvc',
            'mvd', 'mve', 'mvex', 'mvp', 'mvp', 'mvy', 'mxf', 'mxv', 'mys', 'ncor', 'nsv', 'nut', 'nuv', 'nvc', 'ogm',
            'ogv', 'ogx', 'osp', 'otrkey', 'pac', 'par', 'pds', 'pgi', 'photoshow', 'piv', 'pjs', 'playlist', 'plproj',
            'pmf', 'pmv', 'pns', 'ppj', 'prel', 'pro', 'prproj', 'prtl', 'psb', 'psh', 'pssd', 'pva', 'pvr', 'pxv',
            'qt', 'qtch', 'qtindex', 'qtl', 'qtm', 'qtz', 'r3d', 'rcd', 'rcproject', 'rdb', 'rec', 'rm', 'rmd', 'rmd',
            'rmp', 'rms', 'rmv', 'rmvb', 'roq', 'rp', 'rsx', 'rts', 'rts', 'rum', 'rv', 'rvid', 'rvl', 'sbk', 'sbt',
            'scc', 'scm', 'scm', 'scn', 'screenflow', 'sec', 'sedprj', 'seq', 'sfd', 'sfvidcap', 'siv', 'smi', 'smi',
            'smil', 'smk', 'sml', 'smv', 'spl', 'sqz', 'srt', 'ssf', 'ssm', 'stl', 'str', 'stx', 'svi', 'swf', 'swi',
            'swt', 'tda3mt', 'tdx', 'thp', 'tivo', 'tix', 'tod', 'tp', 'tp0', 'tpd', 'tpr', 'trp', 'ts', 'tsp', 'ttxt',
            'tvs', 'usf', 'usm', 'vc1', 'vcpf', 'vcr', 'vcv', 'vdo', 'vdr', 'vdx', 'veg','vem', 'vep', 'vf', 'vft',
            'vfw', 'vfz', 'vgz', 'vid', 'video', 'viewlet', 'viv', 'vivo', 'vlab', 'vob', 'vp3', 'vp6', 'vp7', 'vpj',
            'vro', 'vs4', 'vse', 'vsp', 'w32', 'wcp', 'webm', 'wlmp', 'wm', 'wmd', 'wmmp', 'wmv', 'wmx', 'wot', 'wp3',
            'wpl', 'wtv', 'wve', 'wvx', 'xej', 'xel', 'xesc', 'xfl', 'xlmv', 'xmv', 'xvid', 'y4m', 'yog', 'yuv', 'zeg',
            'zm1', 'zm2', 'zm3', 'zmv')
        return True if filename.split('.')[-1] in videoFileExtensions else False

    def searchTMDB(self,query):
        response = requests.get('https://api.themoviedb.org/3/search/multi?', params={'query':query,
                                                                                      'language':self.config['API Settings']['language'],
                                                                                      'api_key':self.config['API Settings']['apikey']}).content

        try:
            results = simplejson.loads(response)
        except:
            results = simplejson.loads(response.decode('utf-8'))
        return results['results'][0]

    def searchVideoFiles(self,folder):
        videoFiles = []
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for filename in filenames:
                if self.isVideoFile(filename):
                    videoFiles.append((dirpath.replace('\\','/')+'/'+filename))
        return videoFiles




    def checkForDuplicates(self,path,originalPath):
        for file in os.listdir('/'.join(path.split('/')[:-1])):
            if os.path.isfile('/'.join(path.split('/')[:-1])+'/'+file):
                if file.split('.')[0] == path.split('/')[-1].split('.')[0]:
                    self.ui.addText('Duplicate found for: '+originalPath)
                    return True
        self.ui.addText(originalPath+' -> '+path+'\n')
        return False


    def movie_handler(self,tmdbData,path):
        if 'moviefolder' in self.config['Folder Settings']:
            if os.path.isdir(self.config['Folder Settings']['moviefolder']) == False:
                os.mkdir(self.config['Folder Settings']['moviefolder'])
            if 'movie_in_additional_folder' in self.config['Movie Settings']:
                if self.config['Movie Settings']['movie_in_additional_folder'] == 'True':
                    if os.path.isdir(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])) == False:
                        os.mkdir(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title']))
                    if self.checkForDuplicates(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1],path):
                        if self.ui.askDialog('Video already exists','The File "{}" is already existing\nOverwrite?'.format(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/'+self.filterString(tmdbData['title']))):
                            shutil.rmtree(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/')
                            os.mkdir(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/')
                            shutil.move(path,self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1])
                    else:
                        shutil.move(path,self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1])
                else:
                    if self.checkForDuplicates(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1],path):
                        if self.ui.askDialog('Video already exists','The File "{}" is already existing\nOverwrite?'.format(self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title']))):
                            shutil.rmtree(self.config['Folder Settings']['moviefolder']+'/')
                            os.mkdir(self.config['Folder Settings']['moviefolder']+'/')
                            shutil.move(path,self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1])
                    else:
                        shutil.move(path,self.config['Folder Settings']['moviefolder']+'/'+self.filterString(tmdbData['title'])+'.'+path.split('.')[-1])


    def series_handler(self,guessitData,tmdbData,path,tvdbData=''):
        if 'seriesfolder' in self.config['Folder Settings']:
            if os.path.isdir(self.config['Folder Settings']['seriesfolder']) == False:
                os.mkdir(self.config['Folder Settings']['seriesfolder'])
                if int(self.config['Series Settings']['season_number_length']) <= 0:
                    seasonNumber = guessitData['season']
                else:
                    zeros = int(self.config['Series Settings']['season_number_length']) - len(str(guessitData['season']))
                    if zeros < 0:
                        seasonNumber = guessitData['season']
                    else:
                        seasonNumber = zeros*'0'+str(guessitData['season'])
                if int(self.config['Series Settings']['episode_number_length']) <= 0:
                    episodeNumber = guessitData['episode']
                else:
                    zeros = int(self.config['Series Settings']['episode_number_length']) - len(str(guessitData['episode']))
                    if zeros < 0:
                        episodeNumber = guessitData['episode']
                    else:
                        episodeNumber = zeros*'0'+str(guessitData['episode'])
                if self.config['Series Settings']['episode_in_additional_folder'] == 'True':
                    if tvdbData != '':
                        name = tvdbData
                    else:
                        name = 'S'+str(seasonNumber)+'E'+str(episodeNumber)
                    folder = self.config['Folder Settings']['seriesfolder']+'/'+self.filterString(tmdbData['name'])
                    if os.path.isdir(folder) == False:
                        os.mkdir(folder)
                    folder += '/'+self.config['Folder Settings']['seasonfolder']+' '+str(seasonNumber)
                    if os.path.isdir(folder) == False:
                        os.mkdir(folder)
                    folder += '/'+self.config['Folder Settings']['episodefolder']+' '+str(episodeNumber)
                    if os.path.isdir(folder) == False:
                        os.mkdir(folder)
                    if self.checkForDuplicates(folder+'/'+self.filterString(name)+'.'+path.split('.')[-1],path):
                        if self.ui.askDialog('Video already exists','The File "{}" is already existing\nOverwrite?'.format(folder+'/'+self.filterString(name))):
                            shutil.rmtree(folder+'/')
                            os.mkdir(folder+'/')
                            shutil.move(path,folder+'/'+self.filterString(name)+'.'+path.split('.')[-1])
                    else:
                        shutil.move(path,folder+'/'+self.filterString(name)+'.'+path.split('.')[-1])
                else:
                    folder = self.config['Folder Settings']['seriesfolder']+'/'+self.filterString(tmdbData['name'])
                    if os.path.isdir(folder) == False:
                        os.mkdir(folder)
                    folder += '/'+self.config['Folder Settings']['seasonfolder']+' '+str(seasonNumber)
                    if os.path.isdir(folder) == False:
                        os.mkdir(folder)
                    if self.checkForDuplicates(folder+'/'+self.config['Folder Settings']['episodefolder']+' '+str(episodeNumber)+'.'+path.split('.')[-1],path):
                        if self.ui.askDialog('Video already exists','The File "{}" is already existing\nOverwrite?'.format(folder+'/'+self.config['Folder Settings']['episodefolder']+' '+str(episodeNumber))):
                            shutil.rmtree(folder+'/')
                            os.mkdir(folder+'/')
                            shutil.move(path,folder+'/'+self.config['Folder Settings']['episodefolder']+str(episodeNumber)+'.'+path.split('.')[-1])
                    else:
                        shutil.move(path,folder+'/'+self.config['Folder Settings']['episodefolder']+str(episodeNumber)+'.'+path.split('.')[-1])

    def filterString(self,string):
        return string.replace(":"," - ").replace("|"," - ").replace("/"," - ").replace("?","").replace("*","").replace("<"," ").replace(">"," ").replace("\\","")
    def videoNotFound(self,path):
        try:
            if self.ui.askDialog('Video unknown','The Video {} could not be recognized.\nIs it a Series?'.format(path)):
                name = self.ui.inputDialog('Name of the series','What is the name of the series?','Next')
                season = self.ui.inputDialog('Which season','Out of which season is the video?','Next')
                episode = self.ui.inputDialog('Which episode','Which episode is the video?','Next')
                self.series_handler({'season':int(season),'episode':int(episode)},{'name':name},path)
            else:
                title = self.ui.inputDialog('Movietitle','What is the title of the movie?','Next')
                self.movie_handler({'title':title},path)
        except:
            pass

if __name__ == '__main__':
    sorter = videosorter()
    if sorter.isRunnable:
        sorter.run()
        stopTime = 4
        time1 = time.time()
        while time.time()-time1 < stopTime and sorter.ui.stop == False:
            time.sleep(0.25)