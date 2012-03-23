function GitHubAPI(){};

GitHubAPI.Repos = function(username, callback){
	requestURL = "https://api.github.com/users/" + username + "/repos?callback=?";
    console.log(requestURL);
	$.getJSON(requestURL, function(json, status){
        console.log(json);
		callback(json.data.reverse(), status);
	});
}

$(document).ready(function(){
    GitHubAPI.Repos("irskep", function(json, status){
        var content = "";
        $.each(json, function(i){
            projectName = "<a href=\"" + this.url + "\">" + this.name + "</a>";
            projectDescription = this.description;
            stats = this.watchers + " watchers";
            if (this.forks > 0){
                stats += ", " + this.forks + " forks";
            }
            content += "<p class=\"project\">" + projectName + " <span class=\"date\">" + stats + "</span><br/>" + projectDescription + "</p>";
        });
        $("#github-content").html(content);
    })
})
