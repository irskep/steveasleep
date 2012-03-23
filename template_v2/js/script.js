// GitHub API wrapper. http://develop.github.com/
function GitHubAPI(){}

// http://develop.github.com/p/repo.html
GitHubAPI.Repos = function(username, callback){
	requestURL = "http://github.com/api/v2/json/repos/show/" + username + "?callback=?";
	$.getJSON(requestURL, function(json, status){
		callback(json.repositories.reverse(), status);
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
