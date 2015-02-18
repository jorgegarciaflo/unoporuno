/**
*
*
#/usr/bin/env nodeJS
## -*- coding: utf-8 -*-
##
## Copyright (c) 2014 Dominick Makome
**
**/

//Objet mysql
var bdd = require('mysql');
//Appel du module google
var google =  require('google');
//Nouvelle connection à la base de données
var bddConnection = bdd.createConnection({
  host     : 'localhost',
  user     : 'unoporuno',
  password : 'unoporuno',
  database : 'unoporuno'
});

/** Nos différentes fonctions de callBack **/

//Renvoie l'érreur
function getError(err)
{
  console.log("Fail: "+err);
}

//Fonction qui vérifit si le client est connecté
function isConnected (req, res) 
{
  //Si le client est connecté
  if(req.session.username)
  {
    //On lui donne accès
    console.log("Utilisateur connecté sur la page.")
  } 
  else 
  {
    //Sinon on le redirige vers la page de login
    res.redirect("/login");
  }
}
//Teste si l'utilisateur est déjà connecté
function isAlwaysConnected(req,res)
{
  //Si le client est connecté
  if(req.session.username)
  {
    //Une redirection vers la page d'accueil
    res.redirect('/');
  }

}

//Cette fonction détruira la session du client
function deconnected(req,res)
{
  //On détruit les sessions
  req.session.username = "";
  req.session.id = "";
  //Une redirection vers la page d'accueil
  res.redirect('/login');

}

/**
*
* Cette fonction crée des requêtes aléatoirement, ensuite fait appel à la fonction
* Google pour effectuer avec un délai de 60 secondes entre chaque requêtes.
*
*/
function query_bdd(req,res) 
{

  //On récupère nos deux paramètres cruciaux
  var busqueda_id = req.session.busqueda_id;
  var persona_id = req.session.persona_id;

  //On récupère les données dans la table unoporuno_persona
  var recup = "SELECT * from unoporuno_persona WHERE id = ?";

  //Applique la requête
  bddConnection.query(recup,[persona_id],function(err,rows){
      if(err) throw err;
      else
      {
        var result = rows[0].orgs;
        var name = rows[0].name;
        var type_r = rows[0].geo;
        var i = 0;
        //On met chacun des mots dans une partie d'un tableau
        r = result.split(' ');

        for(i = 0; i < r.length; i++)
        {
          //Insertion des requêtes dans la base de données unoporuno_requetes
          insert = "INSERT INTO unoporuno_requete (content,type_r,busqueda_id,persona_id) VALUES(?,?,?,?)";
          bddConnection.query(insert,[name+" "+r[i],type_r,busqueda_id,persona_id]);
        }

        //On récupère la liste des requêtes
        var recup2 = "SELECT * from unoporuno_requete WHERE persona_id = ? && busqueda_id = ?"; 
        //REQUETE d extraction des infos de la table unoporuno_requete
        bddConnection.query(recup2,[persona_id,busqueda_id],function(err, rows) {
            //Si erreur
            if (err) throw err;
            else
            {
            
              for(var i = 0; i < rows.length; i++)
              {

                console.log(rows[i].id+" : "+rows[i].content+" "+rows[i].type_r);
                //attente de 60 seconde entre chaque requete google @Anthony faisait ou presque
                setTimeout(google_req(rows[i].content,req,res),60000);

              }
              
            }
        
        });


      }

  });

}


/**
*
* @Dominik Makome
* Cette fonction crée des requêtes et l'insert dans la table unoporuno requête.
*
*/
function create_req(req,res)
{
  //On récupère nos deux paramètres cruciaux
  var busqueda_id = req.session.busqueda_id;
  var persona_id = req.session.persona_id;

  //On récupère les données dans la table unoporuno_persona
  var recup = "SELECT * from unoporuno_persona WHERE id = ?";

  //Applique la requête
  bddConnection.query(recup,[persona_id],function(err,rows){
      if(err) throw err;
      else
      {
        var result = rows[0].orgs;
        var name = rows[0].name;
        var type_r = rows[0].geo;
        var i = 0;
        //On met chacun des mots dans une partie d'un tableau
        res = result.split(' ');

        for(i = 0; i < res.length; i++)
        {
          //Insertion des requêtes dans la base de données unoporuno_requetes
          insert = "INSERT INTO unoporuno_requete (content,type_r,busqueda_id,persona_id) VALUES(?,?,?,?)";

          bddConnection.query(insert,[name+" "+res[i],type_r,busqueda_id,persona_id]);
        }


      }

  });

}


/**
  * Requete google qui prend en parametre un attribut de la base de données unoporuno_requete avec une recherche efféctuée 
  */
function google_req(content,req,res)
{
        //Maximum de 10 résultats par requete.
        google.resultsPerPage = 10;

        google(content,function(err,next,links){

            //On est bel et bien dans le script google
            console.log("In google script");

            //affiche le rapport d'erreur dans la console
            if (err) console.error(err);
            //Si vaut null, alors aucun résultat par google
            if(next == null)
            {
              res.write("Aucun résultat n'a été trouvé!");
              res.end();
            }     

            //pour chaque resultat on affiche le titre de la page et sa description comme sur google
            for(var i = 0; i<links.length;i++)
            {
                persona_id = req.session.persona_id;
                title =  links[i].title;
                description =  links[i].description;
                link = links[i].link;

                console.log("Insertion n° "+i);
                //Insertion des données dans la base de données unoporuno_snippet
                insert = "INSERT INTO unoporuno_snippet (persona_id,query,title,description,link) VALUES(?,?,?,?,?)";

                bddConnection.query(insert,[persona_id,content,title,description,link]);
            }
        
      });

}

/* GET home page. */
exports.index = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //On récupère la liste des recherches ordonnées par id desc
  var recup = "SELECT * from  unoporuno_busqueda order by id desc";
  //On applique la requête avec la fonction getData qui récupère les données
  bddConnection.query(recup,function(err,rows){

    //Si il y a une érreur on l'affiche
    if(err)
    {
      return getError(err);
    }
    else
    {
      //Différentes données à passer en url à la page
      var data = {title: 'Système de localisation d\'experts sur le web.', 
                  description: 'Liste des recherches récentes.', 
                  layoutFile: 'layout',
                  username: req.session.username,
                  id: req.session.id,
                  data: rows};
      //On envoie les données à la vue
      res.render('index',data);
    }
  });
  
};

/* GET login page. */
exports.login = function(req, res){

  //S'il est déjà connecté on le redirige vers la page d'accueil
  isAlwaysConnected(req,res);
  //Quelques données
  var data = {title: 'Connectez vous afin de pouvoir accéder à toute la plateforme.', 
              description: 'Pas encore connecté, allez y et vous pourrez avoir acccès à tout.', 
              layoutFile: 'layout',
              username: "",
              id: "",
              err:""};
  
  res.render('login',data);
};


/* GET logout. */
exports.logout = function(req, res){
   //On vérifit si le client est connecté
  isConnected(req,res);
  //On le déconnecte
  deconnected(req,res);
};

/* GET register page. */
exports.register = function(req, res){

  //S'il est déjà connecté on le redirige vers la page d'accueil
  isAlwaysConnected(req,res);
  //Erreur générale
  var err = "";
  //Les erreurs
  var errors = new Array();

  //Quelques données
  var data = {title: 'N\'hesitez pas à vous inscrire pour pouvoir accéder à toute la plateforme.', 
              description: 'Inscrivez vous en moins de 60 secondes.', 
              layoutFile: 'layout',
              username: "",
              id: "",
              errors: errors,
              err:err};

  res.render('register',data);
};

/* GET search page. */
exports.search = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //Quelques données
  var data = {title: 'Faites votre recherche ici.', 
              description: 'Rechercher un expert.', 
              layoutFile: 'layout',
              username: req.session.username,
              id: req.session.id,
              err: '',
            };

  res.render('search',data);
};

/* GET search by id. */
exports.persons = function(req, res){
  //On vérifit si le client est connecté
  isConnected(req,res);
  //Récupérons l'id
  var id = parseInt(req.params.id);
  //On prépare notre requête
  var recup = "SELECT * from unoporuno_persona where busqueda_id = ?";
  //On applique la requête avec la fonction getData qui récupère les données
  bddConnection.query(recup,[id],function(err,rows){
      //Si il y a une érreur on l'affiche
    if(err)
    {
      return getError(err);
    }
    else
    {
      //Différentes données à passer en url à la page
      var data = {title: 'Recherche n° '+id, 
                  description: 'Liste des récentes recherches.', 
                  layoutFile: 'layout',
                  username: req.session.username,
                  id: req.session.id,
                  data: rows};

      //On envoie la réponse à une page html
      res.render('persons',data);
    }
  });

};


/* GET details page. */
exports.details = function(req, res){

  //On vérifit si le client est connecté
  isConnected(req,res);
  //On va récupérer les données d'une personne par id
  var id = parseInt(req.params.id);
  //Nom de la personne
  var nameOf = "";
  //On prépare notre requête
  var recup = "SELECT * from unoporuno_snippet where persona_id = ? LIMIT 20";
  //On récupère le nom de la personne
  var recup_name = "SELECT * from unoporuno_persona where id = ?";
  //On applique la requête pour récupérer le nom
  bddConnection.query(recup_name,[id],function(err,rows){

      if(err) throw err;
      else
      {
        //Nom de l'utilisateur
        nameOf = rows[0].name;

        //On applique la requête avec la fonction getData qui récupère les données
        bddConnection.query(recup,[id],function(err,rows){
            //Si il y a une érreur on l'affiche
          if(err)
          {
            return getError(err);
          }
          else
          {

              //Récupération de toutes les langues
              recup2 = "SELECT DISTINCT value from unoporuno_features";
              //Connection pour récupérer les valeurs
              bddConnection.query(recup2,function(error,rows2){

                  if(error) return getError(error);
                  else
                  {

                      //Différentes données à passer en url à la page
                      var data = {title: 'Résultat(s) sur la recherche: "'+nameOf+'"', 
                                  description: 'Différents résultats sur la recherche "'+nameOf+'"',
                                  persona_id:id, 
                                  layoutFile: 'layout',
                                  username: req.session.username,
                                  id: req.session.id,
                                  selected:'',
                                  data: rows,
                                  lang: rows2};

                      //On envoie la réponse à une page html
                      res.render('details',data);
                  }

              });

          }
        });


      }
  });


};

/* @Anthony taf GET google page. */
exports.google = function(req, res){
  //On vérifit si le client est connecté
  isConnected(req,res);
  //On applique l'algorithme pour les requêtes Google
  query_bdd(req,res);
  //On fait une redirection
  res.redirect('/');
};