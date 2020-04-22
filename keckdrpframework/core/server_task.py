"""
@ Deprecated, skwok, April 6, 2020
Marked for removal.

ServerTask, a task to handle HTTP requests.

Created on Jul 19, 2019
                
@author: skwok
"""

import traceback
from keckdrpframework.models.arguments import Arguments
from keckdrpframework.utils.easy_http import EasyHTTPHandler, EasyHTTPServer, EasyHTTPServerThreaded
import io
import matplotlib.pyplot as plt
import json
import socket

import matplotlib

matplotlib.use("Agg")


# from utils.try_wrapper import tryEx


class DRPFServerHandler(EasyHTTPHandler):
    """
    Handles the HTTP requests.
    """

    jsonText = "application/json"
    DRPFramework = None

    def _getParameters(self, qstr):
        for k, v in qstr.items():
            val = v[0]
            try:
                val = int(v[0])
            except:
                try:
                    val = float(v[0])
                except:
                    val = v[0].strip()
            self.__dict__["_http_" + k] = val

    def trigger_event(self, req, qstr):
        self._getParameters(qstr)
        event_name = self._http_event_name
        self.DRPFramework.append_event(event_name, None)
        return json.dumps("OK"), self.jsonText

    def add_new_event(self, req, qstr):
        print("Running add_new_event")
        self._getParameters(qstr)
        print(self.__dict__)
        name = self._http_name
        action = self._http_action
        state = self._http_state
        next = self._http_next
        print("updating event_table")
        self.DRPFramework.pipeline.event_table[name] = (action, state, next)
        return json.dumps("OK"), self.jsonText

    def get_event_table(self, req, qstr):
        print(self.DRPFramework.pipeline.event_table)
        return json.dumps("OK"), self.jsonText

    def get_pending_events(self, req, qstr):
        self._getParameters(qstr)
        events, events_hi = self.DRPFramework.getPendingEvents()
        out = [str(e) for e in events]
        out_hi = [str(e) for e in events_hi]
        return json.dumps({"events": out, "events_hi": out_hi}), self.jsonText

    def add_next_file_event(self, req, qstr):
        self._getParameters(qstr)
        args = Arguments(name=self._http_file_name)
        self.DRPFramework.append_event("next_file", args)
        return json.dumps("OK"), self.jsonText

    def add_create_contact_sheet_event(self, req, qstr):
        self._getParameters(qstr)
        out_dir = self.DRPFramework.config.output_directory
        args = Arguments(dir_name=out_dir, pattern="*.png", out_name="contact_sheet.html", cnt=-1)
        self.DRPFramework.append_event("contact_sheet", args)
        return json.dumps("OK"), self.jsonText

    def _img_to_png(self, imgData):
        h, w = imgData.shape
        imgOut = io.BytesIO()
        dpi = 100
        fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        hEq = hist_equal2d(None, self.DRPFramework.context)
        img = hEq._applyAHEC(imgData).reshape((h, w))

        plt.imshow(img, origin="lower", cmap="gray")

        ax = plt.gca()
        ax.set_axis_off()
        fig.savefig(imgOut, format="png")
        imgOut.seek(0)
        out = imgOut.read()
        plt.close()
        return out

    def _send_imgData(self, imgData):
        self.send_response(200, "OK")
        self.send_header("Expires", "Feb  1 17:17:37 HST 2016")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("Content-Type:", "image/png")
        self.end_headers()

        self.wfile.write(imgData)
        self.wfile.flush()

    # def serveFile (self, req, qstr):
    #    print ("serveFile", req, qstr)
    #    if ".fits" in req:
    #        self._getParameters(qstr)
    #        hdus = open_nowarning(req)
    #        png = self._img_to_png(hdus[0].data)
    #        self._send_imgData(png)
    #        return None, ""
    #    return super().serveFile(req, qstr)

    def echo(self):
        self._getParameters(qstr)
        return json.dumps(qstr), self.PlainTextType


def start_http_server(fw, config, logger):
    port = config.http_server_port
    DRPF_server_handler.DocRoot = config.http_doc_root
    DRPF_server_handler.defaultFile = config.http_defaultFile
    DRPF_server_handler.DRPFramework = fw
    httpd = EasyHTTPServerThreaded(("", port), DRPF_server_handler)
    hostname = socket.gethostname()
    hostname = "127.0.0.1"
    logger.info("HTTPD started %s %d" % (socket.gethostbyaddr(socket.gethostbyname(hostname)), port))
    logger.info("DocRoot is " + DRPF_server_handler.DocRoot)

    try:
        httpd.serve_forever()
        httpd.shutdown()
    except Exception as e:
        traceback.print_exc()
        logger.info("HTTPD terminated")
